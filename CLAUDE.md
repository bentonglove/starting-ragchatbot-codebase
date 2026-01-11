# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A RAG (Retrieval-Augmented Generation) chatbot for querying course materials. Uses ChromaDB for vector storage, Anthropic Claude for AI generation with tool calling, and FastAPI for the backend.

## Commands

**Always use `uv` for dependency management and running commands - never use `pip` directly.**

```bash
# Run the application
./run.sh
# Or manually:
cd backend && uv run uvicorn app:app --reload --port 8000

# Install/sync dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Remove a dependency
uv remove <package-name>

# Test API proxy connection
uv run ai_proxy.py
```

Access at http://localhost:8000 after starting.

## Architecture

```
Frontend (static HTML/JS) → FastAPI (app.py) → RAGSystem → AIGenerator → Claude API
                                                    ↓
                                              ToolManager → VectorStore → ChromaDB
```

### Key Components

**RAG Orchestration (`backend/rag_system.py`)**
- Central coordinator connecting all components
- `query()` method handles the full query flow: history retrieval → AI generation → source tracking

**AI Generation (`backend/ai_generator.py`)**
- Claude API integration with tool calling support
- Two-phase API calls: (1) with tools for search decision, (2) with tool results for final answer
- Supports custom `base_url` for API proxies

**Tool System (`backend/search_tools.py`)**
- Abstract `Tool` base class with `CourseSearchTool` implementation
- `ToolManager` registers tools and executes them when Claude requests
- Tool definitions follow Anthropic's tool calling schema

**Vector Storage (`backend/vector_store.py`)**
- Two ChromaDB collections: `course_catalog` (metadata) and `course_content` (chunks)
- Semantic search with sentence-transformers (`all-MiniLM-L6-v2`)
- Course name resolution via vector similarity matching

**Document Processing (`backend/document_processor.py`)**
- Parses course files (PDF, DOCX, TXT) with expected format:
  - Line 1: `Course Title: ...`
  - Line 2: `Course Link: ...`
  - Line 3: `Course Instructor: ...`
  - Content: `Lesson N: Title` markers followed by lesson content
- Sentence-based chunking with configurable size (800) and overlap (100)

### Data Flow for Queries

1. Frontend sends POST `/api/query` with `{query, session_id}`
2. `app.py` routes to `RAGSystem.query()`
3. `AIGenerator` calls Claude with tool definitions
4. Claude may invoke `search_course_content` tool
5. `ToolManager` executes search via `VectorStore`
6. `AIGenerator` calls Claude again with search results
7. Response returns with answer and sources

## Configuration

Environment variables in `.env`:
- `ANTHROPIC_API_KEY` - Required
- `ANTHROPIC_MODEL` - Model ID (e.g., `claude-haiku-4-5-20251001`)
- `ANTHROPIC_BASE_URL` - Optional, for API proxies

Settings in `backend/config.py`:
- `CHUNK_SIZE`: 800 characters
- `CHUNK_OVERLAP`: 100 characters
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 conversation turns
- `CHROMA_PATH`: `./chroma_db`

## API Endpoints

- `POST /api/query` - Query course materials, returns `{answer, sources, session_id}`
- `GET /api/courses` - Get course statistics
