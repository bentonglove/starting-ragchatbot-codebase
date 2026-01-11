# RAG Chatbot Query Flow Diagram

## Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend<br/>(script.js)
    participant API as FastAPI<br/>(app.py)
    participant RAG as RAGSystem<br/>(rag_system.py)
    participant AI as AIGenerator<br/>(ai_generator.py)
    participant TM as ToolManager<br/>(search_tools.py)
    participant VS as VectorStore<br/>(vector_store.py)
    participant Claude as Claude API

    U->>FE: 輸入問題 "如何成為 Python 高手"
    FE->>FE: 顯示用戶訊息 + 載入動畫
    FE->>API: POST /api/query<br/>{query, session_id}

    API->>RAG: query(query, session_id)
    RAG->>RAG: 獲取對話歷史
    RAG->>AI: generate_response(query, history, tools)

    Note over AI,Claude: 第一次 API 調用 (帶工具定義)
    AI->>Claude: messages.create()<br/>+ tools: [search_course_content]
    Claude-->>AI: tool_use: search_course_content<br/>{query: "Python 高手"}

    Note over AI,VS: 工具執行階段
    AI->>TM: execute_tool("search_course_content", ...)
    TM->>VS: search(query, course_name, lesson)
    VS->>VS: ChromaDB 向量語義搜尋
    VS-->>TM: SearchResults (documents, metadata)
    TM-->>AI: 格式化的搜尋結果

    Note over AI,Claude: 第二次 API 調用 (帶搜尋結果)
    AI->>Claude: messages.create()<br/>+ tool_result: [搜尋結果]
    Claude-->>AI: 最終回答文本

    AI-->>RAG: response
    RAG->>RAG: 保存對話歷史
    RAG-->>API: (answer, sources)
    API-->>FE: {answer, sources, session_id}

    FE->>FE: 移除載入動畫
    FE->>FE: 渲染 Markdown + Sources
    FE->>U: 顯示回答
```

## Architecture Diagram

```mermaid
flowchart TB
    subgraph Frontend["Frontend (Browser)"]
        UI[index.html]
        JS[script.js]
        CSS[style.css]
    end

    subgraph Backend["Backend (FastAPI)"]
        APP[app.py<br/>API Endpoints]

        subgraph RAG["RAG System"]
            RS[rag_system.py<br/>Orchestrator]
            SM[session_manager.py<br/>對話歷史]
        end

        subgraph AI["AI Layer"]
            AG[ai_generator.py<br/>Claude 整合]
            ST[search_tools.py<br/>工具定義]
        end

        subgraph Storage["Storage Layer"]
            VS[vector_store.py<br/>向量操作]
            DP[document_processor.py<br/>文件處理]
            DB[(ChromaDB<br/>向量資料庫)]
        end
    end

    subgraph External["External Services"]
        CLAUDE[Claude API<br/>Anthropic]
    end

    subgraph Data["Data"]
        DOCS[docs/<br/>課程文件]
    end

    UI --> JS
    JS <-->|HTTP| APP
    APP --> RS
    RS --> SM
    RS --> AG
    AG --> ST
    AG <-->|API Call| CLAUDE
    ST --> VS
    VS --> DB
    DP --> VS
    DOCS --> DP

    style Frontend fill:#e1f5fe
    style Backend fill:#fff3e0
    style External fill:#f3e5f5
    style Data fill:#e8f5e9
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        Q[用戶問題]
    end

    subgraph Processing
        direction TB
        P1[1. 解析請求]
        P2[2. 獲取歷史]
        P3[3. Claude 判斷]
        P4{需要搜尋?}
        P5[4. 向量搜尋]
        P6[5. 生成回答]
    end

    subgraph Output
        A[AI 回答]
        S[來源資訊]
    end

    Q --> P1 --> P2 --> P3 --> P4
    P4 -->|是| P5 --> P6
    P4 -->|否| P6
    P6 --> A
    P5 -.-> S

    style Input fill:#c8e6c9
    style Output fill:#bbdefb
```

## Tool Calling Flow

```mermaid
flowchart TB
    subgraph Call1["第一次 Claude API 調用"]
        M1[用戶訊息 + 系統提示]
        T1[工具定義: search_course_content]
        R1{Claude 決定}
    end

    subgraph ToolExec["本地工具執行"]
        TE[ToolManager.execute_tool]
        VS[VectorStore.search]
        CR[ChromaDB 查詢]
        FR[格式化結果]
    end

    subgraph Call2["第二次 Claude API 調用"]
        M2[原始訊息 + 工具結果]
        R2[最終回答]
    end

    M1 --> T1 --> R1
    R1 -->|tool_use| TE
    R1 -->|end_turn| R2
    TE --> VS --> CR --> FR
    FR --> M2 --> R2

    style Call1 fill:#fff9c4
    style ToolExec fill:#f0f4c3
    style Call2 fill:#c8e6c9
```

---

## 如何查看這些圖表

1. **GitHub**: 直接在 GitHub 上查看此文件，會自動渲染 Mermaid 圖表
2. **VS Code**: 安裝 "Markdown Preview Mermaid Support" 擴展
3. **線上工具**: 複製 Mermaid 代碼到 https://mermaid.live/
4. **Obsidian**: 原生支持 Mermaid 圖表
