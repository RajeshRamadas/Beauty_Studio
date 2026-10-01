# Goal Spec — AI Beauty Studio

> Defines what is being built, why, who it serves, and the MVP boundaries. Frontend, backend, API, tests, deployment, and supporting specifications derive from this document.

## 1. Problem Statement

People use inspiration photos to choose hairstyles, makeup, and nail designs, but a reference image shows another person and does not reveal how the look may appear on the user's own photo. Salon consultation can require time and may not provide a visual preview before the appointment.

### Proposed Solution

Build a responsive, mobile-first AI beauty try-on application that accepts:
- A **target photo** of the user.
- A **style-reference image** showing the desired look.

The backend sends both images to an image-editing model with explicit instructions to use the target photo as the base and the reference as style guidance. The user receives a generated preview that can be reviewed and downloaded.

The MVP supports hairstyle, makeup, nail art, and overall beauty look. If the AI provider is unavailable, show a clear failure and retry option; never fabricate a successful result.

The app provides visual inspiration/decision support. It does not guarantee exact identity preservation, exact reference reproduction, salon outcomes, or professional/medical advice.

---

## 2. Goals

### Primary Goals
- Upload a user's photo and a separate style-reference image.
- Apply the requested reference style to the target photo using AI image editing.
- Preserve target identity and scene as closely as the model permits.
- Provide clear validation, processing, success, failure, and retry states.
- Keep provider credentials on the backend and control generation costs.

### Secondary Goals
- Support hairstyle, makeup, nail art, and overall beauty categories.
- Accept optional style description and notes.
- Preview and download generated output.
- Keep architecture provider-independent through an adapter.

### Non-Goals
- Guaranteed identity preservation or exact style reproduction.
- Live video/AR, 3D simulation, or custom model training.
- Salon booking, payments, marketplace, or affiliate commerce in MVP.
- Medical, dermatological, or professional beauty advice.
- Public sharing or automatic publication of user photos.

---

## 3. Target Users

### Guest User
Tests a look by uploading two images and downloading a result. Guest access is suitable for local prototype or controlled, rate-limited trial access.

### Registered User
Uses the app repeatedly and may retain private generation history, subject to retention and deletion controls.

### Administrator / Operator
Manages model configuration, quotas, service health, aggregate usage, and operational incidents. Admin access does not imply unrestricted access to user photos.

### Prototype / Initial Access
- Local prototype may run without login on localhost.
- Public MVP should use authentication or rate-limited guest sessions.
- Roles: `user`, `admin`; no public admin registration.
- API keys remain in backend environment variables/secret manager, never in browser or mobile code.

---

## 4. Core Use Cases

### 1. Apply a Style Reference
- As a user, I upload my photo and a style-reference image.
- I select a category and optionally add style instructions.
- The system treats my photo as the target and the other image as style guidance.
- The system returns a generated result or a clear error; it does not silently swap image roles.

### 2. Review and Save
- I preview the generated image and download it.
- If account history is enabled, I can save it privately and delete it later.
- Failed requests are not recorded as successful results.

### 3. Retry or Adjust
- I can change category, style description, or notes and submit a new request.
- The UI indicates that each new generation may incur API cost.

### 4. Manage Privacy
- I see the processing/privacy notice before upload.
- I can delete saved content; retention rules apply to stored files and metadata.

### 5. Operate the Service
- Admin can view health, aggregate request counts, latency, errors, and usage/cost indicators where available.
- Admin can configure models/limits without seeing secret values; administrative changes are audited.

---

## 5. Core Features (MVP)

### 5.1 Application / Frontend

- Responsive, mobile-first web application for current Android/iOS and desktop browsers.
- Recommended frontend: React + TypeScript; later React Native/Expo can reuse the API.
- Screens: Create Look, Processing, Result, My Looks (if history is enabled), Account/Privacy (if accounts enabled), restricted Admin.
- Create Look workflow:
  1. Upload target photo.
  2. Upload style reference.
  3. Select category.
  4. Optionally enter style description and notes.
  5. Review previews and consent/cost notice.
  6. Submit, monitor status, review result, download/save.
- Both images show previews and replace/remove controls before submission.
- Client validation is for usability; backend repeats every validation.
- Accepted formats: JPEG, PNG, WEBP. Prototype limits: 12 MB per image, minimum 256×256 pixels (configurable).
- Category enum: `hairstyle`, `makeup`, `nail_art`, `overall_beauty`.
- Style description max 300 characters; notes max 500 characters.
- Prevent duplicate submits; show request ID on errors.
- States: empty, invalid, ready, uploading, queued/processing, success, provider error, network error, quota/rate-limit, retry.
- Accessible labels, keyboard navigation, visible focus, contrast, and descriptive errors.
- Do not store selected images in browser storage by default.
- Display notice that AI output is approximate and may alter details beyond the requested style.

### 5.2 Data

Maintain, when persistence is enabled:
- Users/authentication metadata and role.
- Generation request: ID, owner/session, category, prompt text, status, provider/model, timestamps, duration, sanitized error code, usage metadata.
- Image metadata: asset ID, request/owner, purpose (`target`, `reference`, `result`), private storage key, MIME type, size, dimensions, checksum, expiry/deletion status.
- Consent notice version and acceptance timestamp.
- Admin audit events and aggregate metrics.

One user owns many requests. Each request has one target image, one reference image, and zero or one successful output. Store image bytes in private object storage, not ordinary logs or database rows. Local prototype may process in memory and avoid persistent image storage.

### 5.3 User Operations

Users can upload/preview/replace/remove both images, choose category, enter optional instructions, submit generation, view status, preview/download output, retry, and delete saved results if persistence is enabled.

### 5.4 Processing / Business Logic

- Validate auth/session, file size, actual image format, dimensions, category, and text lengths.
- Explicitly identify target and reference roles in provider request.
- Prompt model to apply only relevant reference styling while preserving target identity, face, pose, clothing, and background as closely as possible.
- Default prototype quality setting: `low`; model, size, quality, quotas, and timeout are configurable.
- Enforce per-user/IP rate limits, concurrency limits, and quotas.
- Handle provider timeout, rate limit, unavailable service, access/model errors, and malformed output.
- Validate provider output; return sanitized metadata and image.
- Never promise exact identity preservation or professional results.
- Provider adapter must allow model/provider replacement.

Category behavior:
- Hairstyle: transfer cut, length, styling, and visible color cues, adapted to target hairline/head shape.
- Makeup: transfer colors, placement, finish, and visible makeup style, adapted to target face/skin tone.
- Nail art: transfer design cues; if target nails are not visible, communicate preview limitation rather than implying accuracy.
- Overall beauty: apply relevant hairstyle/makeup cues without copying reference person's identity.

### 5.5 Results / Output

Show generated image, success status, category, optional style description, timestamp, model label where appropriate, download/save action, and “try another look” action. Include an illustrative-result disclaimer.

### 5.6 Error / Unavailable States

- Missing/invalid inputs rejected before provider call.
- Corrupt, unsupported, or oversized files receive actionable errors.
- Provider timeout/unavailable errors are retryable where appropriate.
- Rate limit/quota errors do not trigger repeated automatic retries.
- Unauthorized requests return 401/403; do not leak resource existence.
- Unknown errors show generic message and request ID; logs contain sanitized diagnostics only.
- Never expose stack traces, API keys, raw provider errors, or fake successful outputs.
- Temporary files are removed per retention policy.

### 5.7 Export / Reporting

- MVP output download: PNG.
- Saved results can be deleted by the owner.
- Admin reports: aggregate requests/status, latency, error rates, and provider usage/cost if available.
- Reports exclude image bytes, secrets, and unnecessary personal data; displayed/exported status must match.

---

## 6. Nice-to-Have Features (Post-MVP)

- Native React Native/Expo iOS and Android apps.
- Before/after slider and multiple variations.
- Saved style collections/favorites.
- Optional share links with user opt-in and expiry.
- Salon discovery, recommendations, booking, and offers.
- Advanced segmentation/region controls.
- User feedback on style similarity and identity preservation.
- Provider/model A/B evaluation and localization.

---

## 7. Out of Scope

- Exact identity preservation or guaranteed replication.
- Medical/dermatology advice.
- Real-time AR/video or 3D.
- Salon booking, payments, marketplace, affiliate offers.
- Public social feed or automatic publication.
- Training/fine-tuning on user photos.
- Arbitrary non-beauty image generation.
- Reuse of photos for model training without separate explicit consent.

---

## 8. Success Metrics / Acceptance Outcomes

### Authentication & Access
- Public MVP users authenticate or use controlled guest sessions.
- Users access only their own requests/assets; unauthorized operations are rejected.

### Core Workflow
- User can submit two valid images, choose category, and receive a generated result.
- Target/reference roles remain correct.
- Missing/invalid inputs are rejected; successful result can be downloaded.

### Business Logic
- Provider request contains both images and role-specific instructions.
- Prototype uses low quality by default.
- Category prompts and limits are applied correctly.
- No placeholder is represented as AI success.

### Data
- Request metadata/status is stored when persistence is enabled.
- Images are private and associated with correct owner/request.
- Deletion removes or schedules removal of files and metadata.
- Test photos are synthetic or used with consent.

### External Dependencies
- Provider called only from backend; output validated.
- Provider errors/timeouts do not crash service.
- API key never appears in frontend, logs, or health response.

### Output
- UI shows result/status; downloaded image matches displayed result.
- Cost/processing and AI limitation notices are visible before submission.

### Reliability
- Tests cover invalid input, provider failure, timeout, rate limit, and unauthorized access.
- Timeouts, rate limits, and request IDs are implemented.

---

## 9. Constraints & Assumptions

### Project Constraints
- Initial delivery: responsive web prototype, then production MVP.
- Mobile and desktop browsers; native apps may follow.
- Minimize test cost with low quality and quotas.
- Python backend preferred.
- Hosting platform to be selected.

### External Services
- Initial image provider: OpenAI Images API.
- Private S3-compatible storage if persistence is enabled.
- Authentication and monitoring providers TBD.

### Data Assumptions
- User has rights/permission to upload both images.
- Supported inputs are JPEG/PNG/WEBP.
- Selected model/account supports multi-image editing.
- Results are probabilistic; pricing and availability may change.

### Business Rules
- Target photo is the person/image to transform.
- Reference image is style guidance only; do not copy reference identity.
- Both images required.
- Low quality is default prototype configuration, not a fixed-cost guarantee.
- Inform user that each request may incur provider charges.
- Default prototype retention is transient unless persistence is explicitly enabled.

### Human Responsibility
- User decides whether a look is suitable.
- User obtains permission for another person's image.
- Preview is not a guaranteed salon outcome.
- Operator monitors cost, availability, abuse, and privacy incidents.

---

## 10. Architecture-Level Requirements

### Frontend
- React + TypeScript responsive UI; API remains reusable by future React Native/Expo app.
- Create Look: target uploader, reference uploader, category, optional text, consent/cost notice, submit.
- Processing: status; do not show false percentage. Cancellation only if backend supports it.
- Result: image, download, details, limitation notice, retry/new look.
- My Looks: paginated history and delete if accounts/persistence enabled.
- Account/Privacy: auth, privacy notice, deletion request if public release.
- Admin: restricted aggregate health/usage only.
- Multipart upload; duplicate-submit prevention; accessible controls; no API secrets in bundle/local storage.

### Backend
- Python 3.11+ and FastAPI; Pydantic validation; OpenAI SDK behind provider adapter.
- Auth/authorization, image validation, generation orchestration, status tracking, provider timeouts/error normalization, quotas/rate limits, cost telemetry, optional object storage, structured logs.
- Health/readiness endpoints must not reveal secrets.

### Database
If persistence is enabled, PostgreSQL tables:
- `users`: id, identity/email reference, role, status, created_at.
- `generation_requests`: id, owner, category, style text, notes, status, provider/model, timestamps, duration, error code, usage metadata.
- `image_assets`: id, owner, request, purpose, storage key, MIME, size, dimensions, checksum, expiry/deletion timestamps.
- `consent_records`: owner/session, notice version, accepted_at.
- `audit_events`: actor, action, target, timestamp, sanitized metadata.
Use foreign keys, indexes on owner/status/created_at, and ownership checks. Keep image bytes in private object storage.

### APIs

Base path: `/api/v1`. Multipart for image submission; JSON for metadata. Standard error:
`{"error":{"code":"VALIDATION_ERROR","message":"Human-readable message","request_id":"..."}}`

#### `GET /health`
Liveness response: `{"status":"ok"}`. No secrets or infrastructure details.

#### `GET /ready`
Readiness/dependency status without credentials; non-2xx if unable to accept work.

#### `POST /api/v1/generations`
Multipart fields:
- `target_image` file, required
- `reference_image` file, required
- `category` enum: `hairstyle|makeup|nail_art|overall_beauty`
- `style_description` optional, max 300
- `notes` optional, max 500
- `consent_version` required for public MVP

Production asynchronous response: `202 {"request_id":"uuid","status":"queued","status_url":"/api/v1/generations/{request_id}"}`. Local prototype may respond synchronously with completed result.

#### `GET /api/v1/generations/{request_id}`
Return owned request status (`queued|processing|succeeded|failed`), category, timestamps, sanitized error, model, and authorized result URL if successful. Return 404 for unknown/non-owned IDs.

#### `GET /api/v1/generations`
List authenticated user's history with `limit`, `cursor`, optional category/status filters; metadata only.

#### `GET /api/v1/images/{image_id}`
Return authorized image or short-lived signed URL after ownership/expiry checks.

#### `DELETE /api/v1/generations/{request_id}`
Delete owned request and related assets; return deleted/accepted status.

#### `GET /api/v1/admin/metrics`
Admin-only aggregate counts, statuses, latency, provider errors, and usage/cost when available. No image contents or secrets.

#### Error Codes
- `400 VALIDATION_ERROR`
- `401 UNAUTHENTICATED`
- `403 FORBIDDEN`
- `404 NOT_FOUND`
- `413 FILE_TOO_LARGE`
- `429 RATE_LIMITED` / `QUOTA_EXCEEDED`
- `502 PROVIDER_ERROR`
- `503 SERVICE_UNAVAILABLE`
- `504 PROVIDER_TIMEOUT`

### External Integrations
- OpenAI Images API from backend only.
- Auth/object storage are configurable.
- Provider call includes both images, category prompt, low quality by default, configured size and timeout.
- Normalize errors; store provider/model and usage metadata when available.

### Observability
- Structured logs: request ID, status, duration, provider/model, sanitized error code, byte counts.
- Never log keys, image bytes, signed URLs, or full provider responses.
- Metrics: request count, success/failure, latency, timeouts/rate limits, upload rejections, usage/cost where available.
- Audit admin changes and deletion events.

### Deployment
- Local, staging, production environments.
- Docker Compose for local development; containerized deployment.
- Secrets via environment/secret manager; HTTPS outside localhost.
- Private object storage, lifecycle expiration, metadata backups and recovery plan if persistence is enabled.
- CI runs lint, type checks, unit and API integration tests.

---

## 11. Security & Privacy Requirements

- API key only in backend secret storage.
- HTTPS outside localhost; authenticated user endpoints and ownership checks.
- Validate actual image bytes, not just filename/MIME header.
- File-size, dimension, rate, quota, and concurrency limits.
- Randomized server-side filenames; prevent path traversal.
- Private storage and short-lived signed URLs.
- No image use for model training or unrelated purposes.
- Explicit processing consent and confirmation of rights/permission.
- Document retention and deletion; transient processing by default in prototype.
- Public MVP supports deletion of associated assets/metadata.
- Do not log images or unnecessary personal information.
- Secure CORS, dependency updates, secure cookies/CSRF protections where applicable.
- Review provider data handling and applicable privacy obligations before public launch.

---

## 12. Testing Requirements

### Unit Tests
- Image format/size/dimension/corruption validation.
- Category and text length validation.
- Prompt construction and image-role ordering.
- Status transitions, error mapping, authorization, retention/deletion.

### Integration Tests
- Database and object storage if enabled.
- Provider adapter mocked for success, timeout, rate limit, invalid output.
- Missing API key, auth, ownership, multipart upload, image response.

### End-to-End Tests
- Complete two-image generation and download.
- Missing/unsupported/oversized image.
- Retry after provider failure.
- User A cannot access User B's requests/assets.
- Delete request and verify image is inaccessible.

### Test Data
- Synthetic or consented target/reference pairs for all categories.
- Corrupt/oversized files and provider mock fixtures.
- Human review rubric: style similarity, target identity retention, artifacts, category relevance.
- Real provider tests opt-in and quota-limited because they incur cost.

---

## 13. Delivery Plan

### Phase 1 — Foundation
- Confirm categories/privacy notice; setup frontend and FastAPI.
- Configure backend secrets, health endpoint, upload validation, Create Look UI.

### Phase 2 — Core AI Workflow
- Two-image upload and role-specific prompts.
- Provider adapter, low-quality setting, result/download, loading/error/retry.
- Request IDs, timeouts, basic rate limits.

### Phase 3 — Persistence & Hardening
- Add auth/history if required; private storage and retention/deletion if persisted.
- Add quotas, observability, security review, automated tests.
- Evaluate output across categories and document limitations.

### Phase 4 — Deployment
- Deploy staging with HTTPS, secrets, monitoring, backups, cost controls.
- Run E2E/accessibility acceptance tests and privacy/security readiness review.

---

## 14. Open Questions / Decisions Required

- Web-only MVP or native React Native/Expo apps in initial release?
- Guest generation or mandatory accounts?
- Transient-only images or private saved-look history?
- Retention duration for uploaded and generated images?
- Production model/provider after quality, latency, and cost comparison?
- Per-user/day and guest/IP generation quotas?
- Hosting, database, object storage, and authentication choices?
- Before/after comparison in MVP?
- Consent wording and privacy/compliance review requirements?

Record decisions before implementation when they materially affect scope, architecture, cost, data, or security.

---

## 15. Glossary

| Term | Definition |
|---|---|
| Target photo | User photo that is the base image and whose identity should be retained. |
| Style-reference image | Inspiration image that provides desired beauty-style cues. |
| Style transfer / try-on | AI editing that applies reference style cues to the target photo. |
| Generation request | One submitted operation to create a transformed image. |
| Provider adapter | Backend abstraction isolating app logic from a specific AI provider. |
| Transient processing | Processing without durable application storage. |
| Low quality | Configured output-quality option for economical testing; not a fixed-price guarantee. |

---

## 16. Source / Reference Documents

- User-provided Goal Spec template (`goal(4).md`) for section structure and headings.
- AI Beauty Studio project requirements discussed in this conversation: two-image workflow, beauty categories, generated preview/download, and low-quality testing.
- Technical architecture, API, privacy, and security requirements in this document are proposed project requirements to validate during implementation.

> This Goal Spec is the source of truth for project scope and intended behavior. Detailed specifications derive from it. Resolve conflicts explicitly rather than silently changing the project goal.
