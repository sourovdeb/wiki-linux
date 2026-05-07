# Wiki-Linux System Architecture

> Karpathy 3-Layer LLM Wiki — Personal Knowledge Operating System

## System Diagram

```mermaid
graph TB
    subgraph L1["Layer 1: Raw Sources"]
        Z1[/"📁 raw/my_library/<br>596 PDFs, DOCX"/]
        Z2[/"📁 raw/<br>URLs, articles"/]
        Z3[/"📂 /home/sourov/wiki/<br>personal files"/]
    end

    subgraph L2["Layer 2: Wiki Pages (Markdown)"]
        W1["📝 user/ notes"]
        W2["📝 user/library/<br>converted teaching MDs"]
        W3["📝 system/ docs"]
        W4["📝 docs/ guides"]
        W5["📝 references/"]
    end

    subgraph L3["Layer 3: LLM Interface"]
        OW["🌐 OpenWebUI :8080<br>my_wiki_knowledge KB<br>136+ files, ChromaDB 41MB"]
        OLL["🦙 Ollama :11434<br>mistral, llama3.2, phi3.5"]
        BMO["🔮 Obsidian BMO<br>→ OpenWebUI API"]
        CLI["⌨️ wiki ask<br>CLI interface"]
    end

    subgraph TOOLS["Tools & Automation"]
        KBS["⚙️ wiki-kb-sync<br>hourly timer"]
        ING["🔄 wiki_ingestor<br>markitdown batch"]
        EXT["🧩 openwebui-assistant<br>Chromium extension"]
        SA["🤖 sub_agent<br>autonomous tool calling"]
    end

    subgraph PROMPTS["Prompts (OpenWebUI)"]
        P1["/summary"]
        P2["/plan"]
        P3["/linux"]
        P4["/wiki"]
        P5["/lesson (EFL)"]
        P6["/steelman"]
    end

    %% Data flow
    Z1 -->|"wiki_ingestor<br>markitdown[all]"| W2
    Z2 -->|"ingest.py"| W1
    Z3 -->|"monitor"| W1

    W1 & W2 & W3 & W4 & W5 -->|"wiki-kb-sync<br>(hourly)"| OW

    OW <-->|"OpenAI API"| OLL
    OW -->|"REST API :8080/api/v1"| BMO
    OLL -->|"Ollama API"| CLI
    OW -->|"side panel"| EXT

    SA -->|"tool calls"| OW
    KBS -->|"uploads MDs"| OW
    ING -->|"converts files"| W2

    PROMPTS -.->|"used in"| OW

    style L1 fill:#1a1a2e,stroke:#16213e,color:#e0e0e0
    style L2 fill:#16213e,stroke:#0f3460,color:#e0e0e0
    style L3 fill:#0f3460,stroke:#533483,color:#e0e0e0
    style TOOLS fill:#533483,stroke:#e94560,color:#e0e0e0
    style PROMPTS fill:#e94560,stroke:#533483,color:#fff
```

## Components

### Layer 1 — Raw Sources
| Location | Content | Size |
|----------|---------|------|
| `raw/my_library/` | 596 staged PDFs/DOCX (EFL teaching materials) | ~7.2GB extracted |
| `/home/sourov/wiki/user/my_library/extracted/` | 14 Google Drive exports | 7.2GB |
| `raw/` | Articles, reference docs | varies |

### Layer 2 — Wiki Pages
| Directory | Purpose |
|-----------|---------|
| `user/` | Personal notes, projects, research |
| `user/library/` | Converted teaching materials (markitdown output) |
| `system/` | OS and hardware docs |
| `docs/` | System guides, TinyLLM maintenance |
| `references/` | External references (archwiki, Karpathy) |

### Layer 3 — LLM Interface
| Service | URL | Purpose |
|---------|-----|---------|
| OpenWebUI | `http://127.0.0.1:8080` | Main UI, RAG over `my_wiki_knowledge` |
| Ollama | `http://127.0.0.1:11434` | Local model inference |
| `my_wiki_knowledge` KB | KB ID: `9ead2bd1-bc33-4208-bcff-baffdd890c3b` | 136+ MDs, ChromaDB 41MB |
| Obsidian BMO | via OpenWebUI REST API | In-editor chat |

### Automation Chain
```
[New file appears]
      ↓
wiki_ingestor (watcher/batch)
      ↓ markitdown[all]
user/library/*.md
      ↓
wiki-kb-sync (hourly)
      ↓ OpenWebUI API
my_wiki_knowledge KB
      ↓
All LLMs can query
```

### Services (systemd --user)
| Service | Status | Purpose |
|---------|--------|---------|
| `wiki-monitor` | active | File change monitoring |
| `wiki-sync` | active | Git auto-sync (timer) |
| `wiki-kb-sync` | active | Hourly KB upload |
| `wiki-openwebui` | active | OpenWebUI server |
| `wiki-auto-unzip` | active | Auto-extract downloads |
| `wiki-file-relocate` | active | 30min file organiser |
| `wiki-wallpaper` | active | Wallpaper generation |
| `wiki-boot-popup` | active | Boot status notification |

### OpenWebUI Prompts
| Command | Purpose |
|---------|---------|
| `/summary` | Structured conversation summary |
| `/plan` | Task planning before execution |
| `/linux` | Linux command one-liners |
| `/wiki` | Query my_wiki_knowledge KB |
| `/lesson` | EFL lesson plan generator |
| `/steelman` | Intellectual integrity engine |

### OpenWebUI Tools
| Tool | Purpose |
|------|---------|
| `sub_agent` | Delegate complex tasks to autonomous sub-agent |

## Data Flow

```
Google Drive Exports (7.2GB)
    → /home/sourov/wiki/user/my_library/*.zip (14 zips)
    → bin/wiki-library-extract
    → extracted/ (374 PDFs, 209 DOCX, 178 MP3...)
    → raw/my_library/ (596 staged text files)
    → wiki_ingestor (markitdown[all])
    → user/library/*.md (converted)
    → wiki-kb-sync
    → my_wiki_knowledge KB (OpenWebUI + ChromaDB)
    → All LLM interfaces
```

## Karpathy Alignment

> Based on [Andrej Karpathy's LLM Wiki architecture](bin/history/karpathy-llm-wiki.md)

| Karpathy Concept | This Implementation |
|------------------|---------------------|
| Layer 1: Raw data | `raw/`, extracted Google Drive content |
| Layer 2: Wiki pages | `user/`, `system/`, `docs/` Markdown pages |
| Layer 3: LLM interface | OpenWebUI + my_wiki_knowledge + Ollama |
| Continuous ingestion | wiki_ingestor + wiki-kb-sync |
| Knowledge retrieval | my_wiki_knowledge KB (ChromaDB RAG) |
| Multiple LLM consumers | OpenWebUI UI, Obsidian BMO, CLI, Chromium extension |
