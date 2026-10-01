# AI Beauty Studio — Incremental Development Flow Requirements

> **Document Status**: Active / Source of Truth for Project Roadmap  
> **Version**: 1.0.0  
> **Target System**: AI Beauty Studio (FastAPI Backend, PostgreSQL, S3, Flutter Mobile / Web)

---

## 1. Executive Summary & Strategy

This document defines the formal **Incremental Development Flow** for **AI Beauty Studio**. To ensure rapid validation, cost control, and systemic quality, development is executed in 5 discrete, sequential phases. Each phase establishes a stable foundation for the next.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INCREMENTAL DEVELOPMENT ROADMAP                        │
└─────────────────────────────────────────────────────────────────────────────┘
  Phase 1 [COMPLETED ✅]  ➜ Modular Prototype Core & Cost Engine
  Phase 2 [NEXT 🚀]       ➜ PostgreSQL Persistence & Async Job Queue
  Phase 3                ➜ Authentication, User History & Privacy Controls
  Phase 4                ➜ S3 Object Storage & Security/Cost Hardening
  Phase 5                ➜ Cross-Platform Mobile Application (Flutter)
```

---

## 2. Phase Breakdown & Requirements

### 🟢 Phase 1: Core Modular Backend & Prototype Engine *(COMPLETED ✅)*

#### 1.1 Objective
Establish the foundational FastAPI backend architecture, image validation rules, OpenAI style-reference adapter, and real-time cost calculation telemetry.

#### 1.2 Delivered Components
- **Modular Folder Layout**: `app/` architecture (`api/v1/`, `core/`, `schemas/`, `services/`).
- **Image Preprocessing Service** (`app/services/image_processor.py`):
  - File size validation ($\le 12 \text{ MB}$).
  - Min/Max dimension enforcement ($\ge 256 \times 256 \text{ px}$, downscaled to max $1536 \text{ px}$).
  - EXIF orientation auto-transpose (`ImageOps.exif_transpose`).
  - Supported format validation (`JPEG`, `PNG`, `WEBP`).
- **AI Provider Adapter** (`app/services/provider_adapter.py`):
  - Prompt construction separating Target Photo (base identity) from Style Reference (style guidance).
  - Exact token usage billing calculation + pricing tier fallback.
- **REST Endpoints**:
  - `GET /api/v1/health`
  - `GET /api/v1/ready`
  - `POST /api/v1/generations` (Synchronous prototype execution)
- **Unit Test Suite**: `pytest` coverage for image processor and health endpoints.

---

### 🚀 Phase 2: Database Persistence & Asynchronous Worker Queue *(NEXT MILESTONE)*

#### 2.1 Objective
Transition from synchronous execution to an asynchronous background job queue (`202 Accepted`) with database persistence to prevent HTTP timeouts on long-running AI requests.

#### 2.2 Functional Requirements
1. **Database Schema & Migrations**:
   - Implement PostgreSQL database models using SQLAlchemy or SQLModel.
   - Manage schema evolution using Alembic migrations.
2. **Asynchronous Task Architecture**:
   - Integrate Celery + Redis (or ARQ / FastAPI Background Tasks).
   - `POST /api/v1/generations` MUST save the request with status `queued` and return `202 Accepted` within $< 200 \text{ ms}$.
   - Background worker processes the image edit call and updates status to `succeeded` or `failed`.
3. **Status Polling Contract**:
   - Implement `GET /api/v1/generations/{request_id}` for clients to poll processing status.

#### 2.3 Required Database Models

```sql
-- Core Logical Database Schema
CREATE TABLE users (
    id UUID PRIMARY KEY,
    auth_subject VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generation_requests (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    category VARCHAR(50) NOT NULL,
    style_description TEXT,
    notes TEXT,
    status VARCHAR(50) NOT NULL, -- 'queued', 'processing', 'succeeded', 'failed'
    model_name VARCHAR(100),
    quality VARCHAR(20),
    cost_usd NUMERIC(10, 4),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE image_assets (
    id UUID PRIMARY KEY,
    request_id UUID REFERENCES generation_requests(id),
    role VARCHAR(20) NOT NULL, -- 'target', 'reference', 'result'
    storage_key VARCHAR(500) NOT NULL,
    mime_type VARCHAR(50) NOT NULL,
    byte_size INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.4 Acceptance Criteria
- [ ] `POST /api/v1/generations` returns HTTP 202 with `request_id` and status `queued`.
- [ ] Worker successfully processes background jobs and updates PostgreSQL state.
- [ ] `GET /api/v1/generations/{id}` accurately returns progress status and result base64/URL upon completion.

---

### 🔑 Phase 3: User Authentication, Account History & Privacy Controls

#### 3.1 Objective
Secure endpoints with user authentication, enable private user generation history, and enforce user-controlled data deletion.

#### 3.2 Functional Requirements
1. **Authentication & Authorization**:
   - Implement JWT Bearer token authentication middleware.
   - Enforce strict ownership: User A cannot view, poll, or delete User B's requests or images.
2. **Generation History**:
   - `GET /api/v1/generations`: Return paginated history list for the authenticated user, sorted newest-first.
3. **Privacy & Data Deletion**:
   - `DELETE /api/v1/generations/{request_id}`: Delete request record and associated stored images.
   - Store explicit user consent timestamps (`consent_records`).

#### 3.3 Acceptance Criteria
- [ ] Unauthenticated requests to protected endpoints return `401 Unauthorized`.
- [ ] Attempting to access another user's request returns `403 Forbidden` or `404 Not Found`.
- [ ] Deleting a request purges records and renders image assets inaccessible.

---

### 🛡 Phase 4: S3 Object Storage, Rate Limiting & Production Hardening

#### 4.1 Objective
Transition image binary storage to private Amazon S3 (or S3-compatible storage), enforce rate limits, and provide admin operational monitoring.

#### 4.2 Functional Requirements
1. **Private S3 Storage Adapter**:
   - Upload target, reference, and result images to private S3 buckets.
   - Serve results using short-lived signed URLs (`GET /api/v1/images/{id}`).
2. **Cost Controls & Rate Limiting**:
   - Implement rate-limiting middleware (e.g., max 5 style generations per user per 24 hours).
   - Support environment configurable cost caps.
3. **Admin Telemetry Endpoint**:
   - `GET /api/v1/admin/metrics`: Protected endpoint for aggregate request counts, latency, failure rates, and total provider spend.

#### 4.3 Acceptance Criteria
- [ ] Image bytes are stored in S3, not local disk or PostgreSQL.
- [ ] Image access requires a short-lived signed URL or authorized backend stream.
- [ ] Exceeding generation rate limit returns `429 Too Many Requests`.

---

### 📱 Phase 5: Cross-Platform Mobile Client (Flutter)

#### 5.1 Objective
Deliver a polished, responsive mobile application for iOS and Android built with Flutter.

#### 5.2 Key Screens & Features
1. **Create Look Screen**:
   - Target photo capture/picker + Style reference image picker.
   - Category selector (*Hairstyle*, *Makeup*, *Nail art*, *Overall beauty look*).
   - Optional text instructions & consent check.
2. **Interactive Result Screen**:
   - Before / After slider view.
   - Download result to device gallery + native platform share sheet.
3. **History & Settings Screen**:
   - List of prior generations with status filters.
   - One-tap deletion of stored looks.

---

## 3. Environment & Configuration Matrix

| Variable Name | Default / Example | Purpose |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API provider key |
| `OPENAI_IMAGE_MODEL` | `gpt-image-2.5-flare` | Provider model selection |
| `OPENAI_IMAGE_QUALITY` | `medium` | Quality tier (`low`, `medium`, `high`, `auto`) |
| `MIN_IMAGE_SIDE` | `256` | Minimum image side in pixels |
| `DATABASE_URL` | `postgresql://user:pass@db:5432/beauty` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Async worker task queue broker |
| `STORAGE_TYPE` | `s3` | Storage backend (`local` or `s3`) |
| `S3_BUCKET_NAME` | `ai-beauty-studio-assets` | AWS S3 bucket name |

---

## 4. Verification & Testing Rubric

Every incremental phase must pass the following checks before advancing to the next phase:

1. **Automated Unit & Integration Tests**: `pytest` coverage $> 85\%$.
2. **Security Check**: Zero hardcoded secrets, verified ownership isolation.
3. **Cost & Reliability Check**: No memory leaks, clear error messaging on API failure, accurate cost accounting.
