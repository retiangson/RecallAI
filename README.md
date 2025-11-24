# ✅ **README.md for RecallAI Backend**

*(Enterprise-grade architecture — Domain Driven Design + Dependency Injection)*

---

# # 🚀 RecallAI Backend

A scalable, modular, enterprise-grade backend using **FastAPI**, **Clean Architecture**, **Domain-Driven Design**, and **Dependency Injection** modeled after **KaiHelper’s architecture**.

This backend powers RecallAI — a personal notes + chat + RAG (Retrieval-Augmented Generation) AI assistant.

---

# ## 🧱 Architecture Overview

RecallAI follows a **3-layered clean architecture**:

```
recallai_backend/
│
├── api/                ← Controllers (FastAPI)
│     └── v1/
│
├── business/           ← Application & domain logic
│     ├── interfaces/   ← Service interfaces (Protocols)
│     └── services/     ← Implementations
│     └── service_installer.py  ← DI container
│
├── domain/
│     ├── models/       ← ORM Entities
│     ├── interfaces/   ← Repository interfaces (Protocols)
│     ├── repositories/ ← Concrete repository implementations
│     └── domain_installer.py   ← DI factory for domain layer
│
├── contracts/          ← DTOs / Schemas
│
├── config/             ← Settings, DB engine, security utils
│
├── core/               ← Low-level modules (DB engine)
│
└── bootstrap.py        ← Creates global DI container
```

---

# ## 🎯 Design Principles

### ✔ Clean Architecture

Controllers depend only on service interfaces, not database or repositories.

### ✔ Domain-Driven Design

Repositories encapsulate persistence.
DomainInstaller provides all domain objects.

### ✔ Dependency Injection Container

`ServiceInstaller` binds:

* **IChatService → ChatService**
* **INoteService → NoteService**
* **IAuthService → AuthService**
* **IConversationService → ConversationService**

Controllers resolve services through the container, not manually.

### ✔ Testability

All services depend on interfaces → easy mocking in tests.

### ✔ Scalability

Ready for microservices, background workers, or modular expansion.

---

# ## 🔌 Dependency Injection

## **domain_installer.py**

Responsible for providing:

* DB Session
* UserRepository
* NoteRepository
* ConversationRepository
* EmbeddingService

```python
domain = DomainInstaller()
```

---

## **service_installer.py**

Builds all business-level services and binds them to interfaces.

```python
container = ServiceInstaller(domain)
```

---

## **bootstrap.py**

Creates the global DI instance used by controllers.

```python
from recallai_backend.domain.domain_installer import DomainInstaller
from recallai_backend.business.service_installer import ServiceInstaller

domain = DomainInstaller()
container = ServiceInstaller(domain)
```

---

# ## 🧩 Controllers (FastAPI)

Controllers no longer use:

❌ DB sessions
❌ Repositories
❌ Embedding service
❌ FastAPI Depends

Controllers now ONLY use:

```python
from recallai_backend.bootstrap import container
service = container.get_chat_service()
```

Example:

```python
@router.post("", response_model=ChatResponseDTO)
def ask_chat(dto: ChatRequestDTO):
    service = container.get_chat_service()
    return service.ask(dto)
```

---

# ## 📦 Services

Each service:

* Implements an interface (Protocol)
* Uses domain repository interfaces
* Does not know about DB creation
* Does not know about FastAPI or controllers

Example:

```python
class ChatService(IChatService):
    def __init__(self, conv_repo, note_repo, embedding_service, db):
        self.repo_conv = conv_repo
        self.repo_notes = note_repo
        self.embedding = embedding_service
        self.db = db
```

---

# ## 🏛 Repositories

Repositories implement persistence logic using SQLAlchemy.

Each repo has a matching interface:

```
IUserRepository
INoteRepository
IConversationRepository
```

Services depend only on the interface, not the repository class.

---

# ## 📄 DTOs / Schemas

Kept under `contracts/`, used for:

* Controller request bodies
* Controller response models
* Internal validation

Example:

```
ChatRequestDTO
NoteCreateDTO
ConversationDTOs
```

---

# ## ⚙ Configuration

Located under `recallai_backend/config`:

* `db.py` → SessionLocal, engine
* `config.py` → Settings (OpenAI keys, model names, etc.)
* `security.py` → Hashing utilities

---

# ## 🚀 Running Locally

### **Install dependencies**

```bash
pip install -r requirements.txt
```

### **Run FastAPI**

```bash
uvicorn recallai_backend.main:app --reload
```

API docs:

```
http://localhost:8000/api/docs
```

---

# ## 🧪 Testing Ready

Because everything uses interfaces:

* Mock repositories
* Mock embedding service
* Inject into any service
* Write pure unit tests without DB

---

# ## 🛠 Future Features

This architecture easily supports:

* Vector embeddings (Chroma/Supabase)
* Background workers for ingestion
* Multi-model AI pipelines (Whisper → GPT)
* Multi-database support
* Event-driven flows
* Domain modules (Files, Tags, Folders, Teams, Billing)

---

# ## 🙌 Conclusion

Your RecallAI backend is now:

* Fully modular
* Clean architecture compliant
* DI-driven like enterprise systems
* Scalable for future features
* Easy to maintain and test
* Structured exactly like KaiHelper

This is now a **real enterprise backend**, not a project prototype.