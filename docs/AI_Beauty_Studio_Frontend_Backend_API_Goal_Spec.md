# Goal Spec — AI Beauty Studio (Cross-Platform Mobile App)

> Defines the MVP for a cross-platform beauty try-on application. Flutter frontend, Python backend, API contract, tests, deployment, and supporting specifications derive from this document.

## 1. Problem Statement

People often want to preview a hairstyle, makeup look, nail-art design, or overall beauty style before trying it in person. Today, comparing a style reference with one's own appearance can require manual visualization, salon consultation, or multiple apps. Results may be difficult to preview consistently, and users may not have a convenient way to save or compare generated looks.

### Proposed Solution

Build **AI Beauty Studio**, a mobile-first application for iOS and Android that will:

1. Let users upload or capture a photo of themselves.
2. Let users upload a separate image showing the desired style.
3. Let users choose a transformation category and optionally describe the desired result.
4. Submit both images to an AI image-editing service through a secure backend.
5. Display, save, compare, and download the generated preview.

The primary workflow is: select/capture target photo → select style-reference image → choose category and optional instructions → review consent and submit → view job status → preview result → save/download or try another style.

If the AI provider is unavailable, the application will show a clear failure/retry state and preserve the request metadata where appropriate; it will not fabricate a result.

The application provides **visual inspiration and preview support**. It does not guarantee exact real-world salon outcomes, diagnose skin or hair conditions, or replace professional advice.

---

## 2. Goals

### Primary Goals

- Deliver one Flutter codebase that supports iOS and Android.
- Provide a clear two-image workflow distinguishing the user's target photo from the style-reference image.
- Securely call an image-generation/editing provider from the backend without exposing provider credentials in the app.
- Provide generation status, result preview, download, and user-controlled deletion.
- Validate uploads and handle provider errors, timeouts, and rate limits gracefully.

### Secondary Goals

- Support hairstyle, makeup, nail-art, and overall-beauty categories.
- Provide generation history for signed-in users.
- Allow optional style descriptions and notes.
- Record usage and operational metrics for support and cost monitoring.
- Keep the UI accessible, responsive, and consistent across supported phone sizes.

### Non-Goals

- Building separate native Swift and Kotlin applications for the MVP.
- Training or hosting a custom image-generation model.
- Guaranteeing identity preservation or exact salon outcomes.
- Automated beauty scoring, diagnosis, or medical recommendations.
- Social networking, public galleries, or user-to-user messaging in MVP.
- Salon booking, payments, affiliate commerce, or marketplace features in MVP.

---

## 3. Target Users

### App User

A person who wants to preview a beauty style using their own photo and a separate reference image. They need a simple upload, generation, preview, and save workflow.

### Support / Operations Administrator

An authorized operator who needs to inspect aggregate usage, request status, provider errors, and service health without unnecessary access to user image content.

### Prototype / Initial Access

For the MVP:
- Authentication may be optional for a limited local prototype, but production history and deletion must be associated with an authenticated account.
- Production supports email-based sign-in or a selected identity provider; exact method is an implementation decision.
- Public registration is permitted only after abuse controls, privacy notice, and rate limits are in place.
- Password reset is handled by the selected identity provider or implemented through a secure, expiring reset flow.
- Admin endpoints require a separate privileged role and must not be exposed to ordinary users.

---

## 4. Core Use Cases

### 1. Create a Beauty Preview

- As an app user, I can select a photo of myself and a separate style-reference photo.
- I can choose hairstyle, makeup, nail art, or overall beauty.
- I can add optional instructions describing the intended transformation.
- The system validates both images and submits a generation request.
- If validation or provider processing fails, the app explains the issue and offers a safe retry where possible.

### 2. View and Save a Result

- As an app user, I can see queued, processing, succeeded, or failed status.
- I can view the generated image when processing succeeds.
- I can download/share the result using platform-supported mechanisms, subject to permissions.
- I can delete a generation and its associated stored images according to the retention policy.

### 3. Review Generation History

- As an authenticated user, I can view my prior requests, timestamps, category, and status.
- I can open a successful result while it remains available.
- I cannot access another user's request or image.

### 4. Monitor Service Health

- As an administrator, I can view aggregate generation counts, failure counts, latency, and provider availability.
- The system exposes health/readiness checks and structured logs.
- Admin views do not reveal image contents by default.

---

## 5. Core Features (MVP)

### 5.1 Application — Frontend

**Technology:** Flutter (Dart), targeting supported iOS and Android versions. Use a maintainable state-management approach (e.g. Riverpod or Bloc; choose one before implementation), typed API models, and environment-specific configuration.

**Main screens:**
1. **Welcome / Consent:** brief explanation, privacy notice, and consent to process uploaded images.
2. **Create Preview:** target-photo picker/camera action, reference-image picker, category selection, optional description/notes, and submit button.
3. **Image Review:** separate previews and replace/remove controls for each image before submission.
4. **Generation Progress:** request status, progress messaging (without inventing a percentage), cancel/delete option if supported, and retry on recoverable errors.
5. **Result Preview:** generated image, category, timestamp, before/reference/result presentation, download/share, and create-another action.
6. **History:** list of the user's prior generations with status and date; empty and loading states.
7. **Settings / Privacy:** account controls, consent information, retention/deletion actions, and support links.
8. **Admin/Operations:** not part of the consumer mobile app MVP; operational metrics may be provided through a protected web/admin interface later.

**Frontend behavior:**
- Mobile-first layouts, safe-area handling, accessible labels, adequate touch targets, and support for portrait orientation.
- Image picker and camera permissions requested only when needed; explain why permission is needed.
- Validate file type and size before upload where possible; backend remains authoritative.
- Show upload progress when available, otherwise a clear submitting state.
- Prevent duplicate submissions while a request is being created.
- Do not display false progress percentages. Poll status with bounded intervals/backoff or use a future push mechanism.
- Handle offline state, expired authentication, permission denial, empty history, missing result, and provider failure.
- Keep API base URL and public configuration environment-specific; no provider API keys or secrets in the app bundle.

### 5.2 Data

The system will maintain:
- **User:** identifier, authentication subject, account timestamps, role/status.
- **Generation Request:** request ID, user ID, category, optional prompt/notes, status, timestamps, error code (safe public code), provider/model metadata where appropriate.
- **Image Asset:** asset ID, request ID, role (`target`, `reference`, `result`), private storage key, MIME type, byte size, dimensions, created/deleted timestamps.
- **Consent Record:** user/request association, consent version, timestamp.
- **Usage Event:** request ID, user ID, processing duration, provider outcome, usage/cost metadata when available.
- Relationships: one user has many generation requests; one request has target/reference assets and zero or one result asset; consent and usage records reference the relevant user/request.

### 5.3 User Operations

Users can:
- Capture or choose target and reference images.
- Replace or remove either image before submission.
- Select a transformation category and enter optional instructions.
- Submit a generation request and view its status.
- View and download/share successful results.
- Browse their own history and delete their requests.
- Sign in/out and manage account/privacy settings as supported by the chosen auth provider.

### 5.4 Processing / Business Logic

The backend will:
- Validate authentication, consent, category, image MIME type, size, dimensions, and ownership.
- Accept target and reference images as separate inputs and preserve their roles in the provider prompt.
- Use a configurable AI provider/model adapter; provider selection and model names are environment configuration, not hardcoded into the mobile app.
- Default to a cost-conscious quality setting configurable on the server.
- Create a request record and process generation asynchronously where provider latency makes a synchronous request unsuitable.
- Track status: `queued`, `processing`, `succeeded`, `failed`, and optionally `cancelled`.
- Enforce per-user and per-IP rate limits/quotas.
- Store generated outputs in private object storage and issue short-lived authorized access URLs or proxy image access through the backend.
- Retry only transient provider/network errors with bounded retries and idempotency safeguards.
- Never silently substitute an unrelated image or claim a generation succeeded without a validated output.
- Apply retention and deletion rules to uploaded and generated images.

### 5.5 Results / Output

After a successful operation, display:
- Generated result image.
- Generation request ID (for support), category, and creation/completion timestamp.
- Status and optional non-sensitive style description.
- Actions to download/share, create another preview, or delete.
- Clear note that generated previews may differ from real-world results.

### 5.6 Error / Unavailable States

- Invalid/missing image: explain which image needs correction.
- Unsupported file type or file too large: show supported formats/limit.
- Authentication/authorization failure: request sign-in or explain access denial.
- Rate limit/quota exceeded: show retry guidance without exposing internal limits unnecessarily.
- Provider timeout/unavailable: mark request failed or retrying according to policy; show retry option.
- Missing/expired result URL: request a fresh authorized URL or show that the result has expired.
- Network interruption: retain form state where feasible and allow user-initiated retry.
- Do not expose stack traces, provider credentials, internal URLs, or sensitive provider responses.
- Log sanitized error details with correlation/request ID.

### 5.7 Export / Reporting

- MVP output export: save image to device and use native share sheet where supported.
- History list is displayed in-app; CSV/PDF reporting is not required for consumers.
- Admin metrics may be exported later; if added, exports must match displayed filters and values.
- Exported image should be the generated output, not the target/reference image unless explicitly selected by the user.

---

## 6. Nice-to-Have Features (Post-MVP)

- Side-by-side or slider comparison of original and generated images.
- Saved style collections and favorites.
- Push notifications when long-running generations complete.
- Multiple generated variations per request.
- Hair color, makeup intensity, and other structured controls.
- Salon discovery, booking, offers, and affiliate links.
- Subscription/credits and in-app purchases.
- Web application using the same backend API.
- Additional AI providers with configurable routing and cost/quality policies.
- Localization and additional accessibility enhancements.

---

## 7. Out of Scope

- Native-only Swift/Kotlin implementation.
- Custom model training, fine-tuning, or GPU infrastructure in MVP.
- Medical/dermatological assessment or claims.
- Guaranteed exact identity, texture, color, or salon result.
- Public sharing feed or public user-generated gallery.
- Salon appointment booking, payments, commerce, and affiliate tracking.
- Automatic posting to social networks.
- Unmoderated public uploads or public access to private images.
- Any use of user images beyond the stated processing purpose without separate consent.

---

## 8. Success Metrics / Acceptance Outcomes

### Authentication & Access
- Authenticated users can create and retrieve only their own requests.
- Unauthorized and cross-user access attempts are rejected.
- Admin operations require privileged authorization.

### Core Workflow
- User can select target and reference images, choose a category, submit, and view a successful result in supported test conditions.
- Invalid inputs are rejected with actionable messages.
- Request status transitions are reflected in the UI.

### Business Logic
- Target and reference image roles are preserved throughout the API/provider workflow.
- Duplicate submission protection and idempotency behavior are tested.
- Boundary file sizes, dimensions, MIME types, rate limits, and ownership checks behave as specified.
- Provider failures do not produce a false success state.

### Data
- Requests, assets, consent, and usage metadata are associated correctly.
- User deletion removes or schedules deletion of associated image assets and records according to policy.
- Sample users and test images are available in non-production environments.

### External Dependencies
- Provider adapter submits the correct inputs and handles validated output.
- Provider timeout, rejection, rate limit, and unavailable states are tested.
- Provider credentials are not present in client builds or logs.

### Output
- UI displays generated result, status, category, and timestamp.
- Download/share uses the generated result.
- Expired or deleted images are handled clearly.

### Reliability
- Expected network, API, database, storage, and provider errors are handled without app crashes.
- Structured logs include correlation IDs but exclude image bytes, secrets, and unnecessary personal data.
- Key operations and failures are measurable.

---

## 9. Constraints & Assumptions

### Project Constraints

- **Timeline:** staged implementation; timeline to be agreed.
- **Team size:** initially small development team / individual developer.
- **Target platform:** iOS and Android mobile; optional admin web interface later.
- **Budget:** image generation has per-request provider cost; quotas and quality settings must be configurable.
- **Technology:** Flutter frontend; Python FastAPI backend; PostgreSQL; private object storage; Docker-based deployment is preferred.

### External Services

- AI image-editing/generation provider supplies transformation capability.
- Authentication provider may supply identity and password management.
- Object storage stores private input/output images.
- Push notification provider is optional and post-MVP.

### Data Assumptions

- Users provide a target photo they are authorized to use and a style reference they are authorized to use.
- Initial supported image formats: JPEG, PNG, and WEBP.
- Proposed initial limit: 12 MB per image; minimum dimensions 256 × 256 pixels. These are configurable product defaults to validate during implementation.
- Images may be resized/compressed for upload subject to quality and provider requirements.
- Generated output quality and fidelity depend on the selected provider/model and input images.

### Business Rules

- Categories: `hairstyle`, `makeup`, `nail_art`, `overall_beauty`.
- Target image is the person/photo to transform; reference image indicates the desired style.
- User instructions are optional and length-limited.
- Consent is required before images are sent to the AI provider.
- Generation results are private to the owning user.
- Retention duration, account deletion behavior, and provider data handling must be documented before production launch.

### Human Responsibility

- Users decide whether a generated style is suitable and whether to consult a professional.
- The system must not claim exact or guaranteed real-world results.
- Users are responsible for having rights/permission to upload images.
- The product must provide a privacy notice explaining processing, storage, retention, and deletion.

---

## 10. Architecture-Level Requirements

### 10.1 Frontend

**Framework:** Flutter / Dart. Use a single shared codebase with platform-specific adapters only where required.

**Suggested modules:**
- `app`: app bootstrap, routing, theme, environment configuration.
- `features/auth`: sign-in, sign-out, session state.
- `features/create`: image selection, category, instructions, consent, submission.
- `features/generation`: request status, polling, retry, cancellation if supported.
- `features/result`: preview, download/share, delete.
- `features/history`: paginated user's generation list.
- `features/settings`: privacy, account, help.
- `core/network`: API client, auth interceptor, error mapping, request IDs.
- `core/media`: camera/gallery permissions, image validation, compression, local cache.
- `core/widgets`: reusable buttons, upload cards, status indicators, error/empty/loading states.

**Frontend requirements:**
- Typed request/response models and centralized API client.
- Secure token storage using platform-secure storage.
- Do not persist sensitive images in an unprotected cache; clear temporary files according to policy.
- API requests use HTTPS.
- Support current supported iOS/Android versions as decided during release planning.
- UI tests for main navigation and create-preview workflow.

### 10.2 Backend

**Framework:** Python FastAPI with Pydantic request/response schemas.

**Suggested services/modules:**
- API/router layer: versioned REST endpoints.
- Authentication/authorization middleware/dependencies.
- Generation service: request lifecycle and orchestration.
- Provider adapter: isolates provider-specific SDK/API details.
- Image validation service: MIME sniffing, dimensions, size, safe decoding.
- Storage service: private object storage operations and signed URL generation.
- Repository/data layer: PostgreSQL access and transactions.
- Background worker/queue: asynchronous generation processing (recommended for production).
- Rate limiting/quota service.
- Observability: structured logs, metrics, tracing/correlation IDs.

**Backend requirements:**
- Keep business rules and provider credentials server-side.
- Validate all client inputs; never trust client-provided user IDs or storage keys.
- Enforce object ownership for read/delete operations.
- Use idempotency keys for request creation where appropriate.
- Keep provider calls outside database transactions.
- Set timeouts, bounded retries, and concurrency limits.
- Return stable public error codes; log detailed internal errors securely.

### 10.3 Database

**Technology:** PostgreSQL.

Core tables (logical model):
- `users(id, auth_subject, role, status, created_at, updated_at)`
- `generation_requests(id, user_id, category, style_description, notes, status, idempotency_key, error_code, provider_name, model_name, created_at, started_at, completed_at, deleted_at)`
- `image_assets(id, request_id, role, storage_key, mime_type, byte_size, width, height, created_at, deleted_at)`
- `consent_records(id, user_id, request_id, consent_version, consented_at)`
- `usage_events(id, request_id, user_id, provider_status, duration_ms, usage_metadata, created_at)`

Constraints/indexes:
- Foreign keys for user/request relationships.
- Index `(user_id, created_at DESC)` for history.
- Index `(status, created_at)` for worker/admin queries.
- Unique `(user_id, idempotency_key)` when idempotency key is supplied.
- Restrict role values and status/category values at application and/or database level.
- Store image bytes in object storage, not PostgreSQL.

### 10.4 API Interface

**Base path:** `/api/v1`  
**Transport:** HTTPS REST; JSON for metadata; multipart form-data for image upload.  
**Authentication:** Bearer access token for user endpoints; privileged role for admin endpoints.  
**Time format:** ISO 8601 UTC timestamps.  
**IDs:** UUID or opaque non-guessable identifiers.  
**Pagination:** cursor-based or limit/offset; choose one consistently (MVP may use limit/offset with maximum page size).  
**Correlation:** accept or generate `X-Request-ID`; return it in responses and logs.

#### Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check including required dependencies |
| POST | `/api/v1/generations` | Create generation request with target/reference images |
| GET | `/api/v1/generations` | List current user's requests |
| GET | `/api/v1/generations/{request_id}` | Get status/details for owned request |
| DELETE | `/api/v1/generations/{request_id}` | Delete request and associated assets |
| GET | `/api/v1/images/{image_id}` | Obtain authorized image access/stream |
| GET | `/api/v1/admin/metrics` | Protected aggregate operational metrics |

#### `POST /api/v1/generations`

Content type: `multipart/form-data`

Fields:
- `target_image` — required file; user's photo to transform.
- `reference_image` — required file; desired style reference.
- `category` — required enum: `hairstyle`, `makeup`, `nail_art`, `overall_beauty`.
- `style_description` — optional text; proposed maximum 300 characters.
- `notes` — optional text; proposed maximum 500 characters.
- `consent_version` — required string identifying the consent notice accepted.
- `Idempotency-Key` — recommended request header to prevent accidental duplicate creation.

Success: `202 Accepted` when queued, returning a request ID and initial status.

Example response:
```json
{
  "request_id": "uuid",
  "status": "queued",
  "category": "hairstyle",
  "created_at": "2026-10-01T08:00:00Z",
  "status_url": "/api/v1/generations/uuid"
}
```

#### `GET /api/v1/generations/{request_id}`

Returns request metadata and status. On success, includes a result image identifier or authorized result URL with limited lifetime.

Example:
```json
{
  "request_id": "uuid",
  "status": "succeeded",
  "category": "hairstyle",
  "created_at": "2026-10-01T08:00:00Z",
  "completed_at": "2026-10-01T08:00:24Z",
  "result": {
    "image_id": "uuid",
    "url": "short-lived-authorized-url"
  }
}
```

#### `GET /api/v1/generations`

Returns the authenticated user's requests, newest first, with pagination metadata. Must not return other users' records.

#### `DELETE /api/v1/generations/{request_id}`

Deletes or schedules deletion of the request and related input/output assets. Returns `204 No Content` on accepted deletion. If asynchronous deletion is used, document its completion semantics.

#### `GET /api/v1/images/{image_id}`

Returns an authorized image stream or a short-lived access URL. Verify the image belongs to the authenticated user. Never expose raw storage keys.

#### `GET /api/v1/admin/metrics`

Admin-only aggregate counts, success/failure rates, processing latency, provider error categories, and usage totals where available. No image payloads.

#### Common Error Contract

```json
{
  "error": {
    "code": "IMAGE_TOO_LARGE",
    "message": "The selected image exceeds the allowed file size.",
    "request_id": "correlation-id",
    "details": {}
  }
}
```

Expected HTTP statuses:
- `400` invalid request or unsupported category.
- `401` missing/invalid authentication.
- `403` insufficient permissions or ownership denied.
- `404` request/image not found.
- `413` upload exceeds configured limit.
- `415` unsupported media type.
- `422` image cannot be decoded or fails dimension validation.
- `429` rate limit/quota exceeded.
- `500` unexpected internal error (generic message only).
- `502` provider returned an invalid/upstream failure response.
- `503` provider or required dependency unavailable.
- `504` provider processing timeout.

### 10.5 External Integrations

- **AI image provider:** backend-only credentials; provider adapter maps target/reference/category/instructions to provider request. Validate output format and dimensions before storage.
- **Object storage:** private bucket/container; encryption at rest; short-lived signed URLs or backend proxy; lifecycle deletion policy.
- **Authentication:** JWT/OIDC validation or selected managed identity provider.
- **Optional telemetry:** error monitoring and metrics with sensitive-data filtering.

Failure behavior: mark request failed with a stable public code, retain safe diagnostic metadata, and allow retry only when the operation is recoverable and within quota.

### 10.6 Observability

- Structured JSON logs with timestamp, severity, environment, request ID, generation ID, and safe error code.
- Metrics: request count, success/failure rate, queue depth, provider latency, API latency, upload rejection counts, storage errors, and estimated provider usage/cost when available.
- Audit events for consent, generation creation, deletion, and admin access.
- Do not log image bytes, access tokens, API keys, signed URLs, or full sensitive prompts by default.
- Alerts for elevated failure rate, queue backlog, provider outage, and storage errors.

### 10.7 Deployment

- Environments: local development, staging, production.
- Containerize FastAPI API and background worker; use managed PostgreSQL and private object storage where feasible.
- Store secrets in environment-specific secret manager; never commit `.env` or credentials.
- CI checks: formatting, linting, unit tests, dependency/security checks, and container build.
- Database migrations run through controlled deployment steps.
- Backups and recovery policy for metadata; image lifecycle/retention policy for object storage.
- Flutter builds configured separately for iOS and Android signing/release workflows.
- Production requires HTTPS, rate limits, monitoring, and privacy/retention policy review.

---

## 11. Security & Privacy Requirements

- Require explicit consent before submitting images for AI processing.
- Explain purpose, provider processing, storage, retention, and deletion in a readable privacy notice.
- Use HTTPS for all app/backend communication.
- Keep AI provider credentials and storage credentials on the server.
- Store authentication tokens using platform-secure storage.
- Validate MIME type by content, decode images safely, enforce file size/dimension limits, and reject malformed files.
- Restrict access to requests/images by authenticated owner; enforce admin role checks.
- Use private object storage and short-lived signed URLs or authenticated image proxy.
- Apply rate limits, quotas, upload limits, and abuse controls.
- Avoid logging images, tokens, secrets, signed URLs, or unnecessary personal data.
- Provide user-initiated deletion and define retention/deletion timelines before production.
- Document whether the external AI provider retains submitted content and configure provider privacy controls where available.
- Follow applicable privacy and app-store requirements; obtain legal review before production launch.

---

## 12. Testing Requirements

### Unit Tests
- Category and text validation.
- File size, MIME, decoding, and dimension validation.
- Status transition rules.
- Ownership and authorization helpers.
- Provider request mapping and error mapping.
- Retry/idempotency logic.

### Integration Tests
- PostgreSQL repositories and migrations.
- Object storage upload/read/delete and signed URL expiry.
- Authentication and role enforcement.
- Provider adapter using mocked responses and controlled test credentials.
- API multipart upload and response schema.
- Flutter API client and error mapping.

### End-to-End Tests
- Create preview with valid target/reference images.
- Reject missing, oversized, malformed, and unsupported images.
- Poll queued/processing/succeeded/failed states.
- Open result, download/share, and delete.
- Verify one user cannot read/delete another user's request.
- Simulate offline network, provider timeout, provider rate limit, and expired image URL.

### Test Data
- Synthetic/test images with appropriate usage rights.
- Expected category and status cases.
- Boundary file sizes and dimensions.
- Mock provider success, invalid output, timeout, 429, and 5xx responses.
- No real user images in automated test fixtures unless explicit permission and safeguards exist.

---

## 13. Delivery Plan

### Phase 1 — Foundation
- Confirm supported OS versions, auth method, retention policy, provider, and image limits.
- Create Flutter app structure, navigation, theme, and reusable UI components.
- Create FastAPI project, configuration, health endpoints, PostgreSQL schema, and migrations.
- Configure private object storage and local development environment.

### Phase 2 — Core Functionality
- Implement image picker/camera and image review UI.
- Implement authenticated multipart generation endpoint and validation.
- Implement provider adapter and asynchronous job processing.
- Implement status polling, result preview, and authorized image delivery.
- Add user history and deletion.

### Phase 3 — Validation & Reporting
- Add robust error mapping, quotas, idempotency, structured logs, metrics, and audit events.
- Complete unit, integration, and end-to-end tests.
- Validate provider cost controls and retention/deletion behavior.
- Conduct privacy and security review.

### Phase 4 — Deployment
- Deploy staging API, worker, database, and object storage.
- Build and test iOS/Android release candidates.
- Configure production secrets, HTTPS, monitoring, backups, and CI/CD.
- Complete app-store metadata, privacy disclosures, and final acceptance testing.

---

## 14. Open Questions / Decisions Required

- Which AI image provider/model and permitted data-retention settings will be used in production?
- Is authentication required before the first generation, or can users try a limited guest flow?
- Which sign-in method will be used (email, Apple, Google, or managed identity)?
- What are final per-image size/dimension limits and supported image formats?
- What is the image retention period, and what happens when a user deletes their account?
- Should generation run through a background queue from the first MVP release?
- What are per-user quotas, retry limits, and budget alerts?
- Which minimum iOS and Android versions will be supported?
- Is an admin web console required for MVP, or are protected metrics endpoints sufficient?
- Which app name, branding, and privacy/legal copy are final?

Decisions that materially affect architecture, data, security, or scope must be recorded before implementation.

---

## 15. Glossary

| Term | Definition |
|---|---|
| **Target image** | The user's photo that the AI transformation should edit. |
| **Reference image** | An image showing the desired hairstyle, makeup, nail art, or beauty style. |
| **Generation request** | A tracked request to produce an AI-edited preview. |
| **Provider adapter** | Backend component that isolates provider-specific API details. |
| **Signed URL** | Time-limited URL granting access to a private stored image. |
| **Idempotency key** | Client-supplied key used to prevent duplicate request creation after retries. |
| **Consent version** | Identifier for the privacy/processing notice accepted by the user. |

---

## 16. Source / Reference Documents

- User-provided Goal Spec template (`goal(5).md`).
- AI Beauty Studio product concept and prior requirements discussions: two-image style-reference workflow for hairstyle, makeup, nail art, and overall beauty.
- Technology direction established for this iteration: Flutter mobile frontend, Python FastAPI backend, PostgreSQL, private image storage, and a server-side AI provider integration.

> This Goal Spec is the source of truth for the project scope and intended behavior. Detailed frontend, backend, API, database, testing, and deployment specifications should derive from this document. Where a detailed specification conflicts with this document, resolve the conflict explicitly rather than silently changing the project goal.
