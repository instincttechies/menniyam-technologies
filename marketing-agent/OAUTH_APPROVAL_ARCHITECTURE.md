# Menniyam Marketing Agent: OAuth and approval-first publishing architecture

## Confirmed targets
- LinkedIn: Menniyam Technologies **organization/company page** (not a personal profile).
- Instagram: Menniyam Technologies **Professional account**.
- Posting cadence: **two posts per day per platform**, Asia/Kolkata timezone (proposed slots 09:00 and 18:00 IST; changeable).
- Publication policy: **explicit human approval for each final platform-specific post**. Approval is not permission to publish any revised version.
- No post may be sent to a platform until account connection, scopes, ownership, security and publishing API integration have been tested.

## Provider OAuth design (not yet implemented)
1. Authorized operator signs in to the Menniyam admin console via OIDC. Enforce MFA and role-based access (marketing editor, approver, admin). Avoid a shared API key in production.
2. Operator clicks **Connect LinkedIn** or **Connect Instagram**. Server creates a cryptographically random state and PKCE verifier/challenge where supported, bound to authenticated user, tenant, intended provider and redirect URI. Store short-lived single-use state in Redis/database. Redirect to the **official provider authorization endpoint**.
3. Callback validates state, logged-in session, tenant and expiry, exchanges authorization code server-side, verifies granted scopes and discovers target accounts. Never expose tokens to frontend or log credentials.
4. LinkedIn: select the correct organization URN and verify operator has permitted organization posting role and app has approved organization publishing access/scopes. LinkedIn organization publishing may require additional product access and review.
5. Instagram: use the currently supported Meta Instagram API login path, confirm Professional account eligibility and required publishing permissions. A linked Facebook Page may be required depending on the chosen API flow. Confirm current Meta app permissions and review requirements before activation.
6. Encrypt access and refresh tokens (where issued) at rest using managed KMS, rotate/refresh as supported, record expiry and scopes. Provide account disconnect/revoke and periodic validation.
7. Restrict publishing to an explicit allowlist of verified Menniyam account identifiers; prevent arbitrary account_id supplied by a client from becoming a publication destination.

## Content lifecycle
- draft -> pending_approval -> approved -> scheduled -> published
- pending_approval -> rejected -> draft (on edit) -> pending_approval
- Any edit after approval resets status to draft and invalidates prior approval.
- Approval record includes actor identity, timestamp, platform, account, caption, media asset digest and content fingerprint.
- Publishing worker checks approval fingerprint, authorized destination, media validity, token validity, scheduled time and idempotency key immediately before sending.
- Approved posts may be scheduled. Scheduling never bypasses approval.
- Revocation, rejection or editing must cancel any queued job; re-check approval at execution time.
- Publishing should use a transactional outbox and unique idempotency key to avoid duplicate posts on retries. Record provider post ID, timestamp, errors and audit trail.

## Content calendar and AI pipeline (planned)
- Generate 2 LinkedIn + 2 Instagram **platform-specific drafts daily**; no auto-approval.
- Professional white corporate visual identity, Menniyam branding, Python Zero to Hero training and educational content.
- Each draft: caption, hashtags, CTA, approved banner asset, target account, proposed schedule, campaign identifier, owner and review status.
- Calendar statuses: draft, pending approval, approved, scheduled, published, rejected, failed.
- Default proposed times: 09:00 and 18:00 Asia/Kolkata, subject to owner confirmation.
- AI generation must never fabricate course guarantees, student outcomes, placement promises, or testimonials.

## Required production storage
- users, tenants, memberships, roles
- provider_connections (encrypted token references, account IDs, scopes, expiry, connection status)
- posts, media_assets, approvals, scheduled_jobs, publish_attempts, audit_events
- Persist in PostgreSQL with tenant isolation, row-level controls as appropriate, encrypted secrets and backups.
- Background queue/worker with reliable retries and observability.

## Current branch limitations
- Existing FastAPI endpoints remain an **in-memory developer MVP**, not a deployed social publisher.
- `AGENT_ADMIN_KEY` is an MVP-only gate. Without it, all write/read draft operations fail closed (503); invalid key returns 401. Production must use authenticated users with OIDC/RBAC and an approver identity that cannot be forged by a caller.
- No live OAuth redirects/callbacks, provider tokens, connected accounts, AI/banner generation, persistent scheduler or real platform publisher exist yet.
- `POST /drafts/{id}/publish` deliberately returns 501 even when approved.
- The scheduling endpoint stores a proposed time in memory; it does not run background jobs.
- Do not expose the MVP API publicly without stronger auth, rate limiting, CSRF considerations for browser sessions, persistence and audits.

## Rollout acceptance checklist
- [ ] Create/configure LinkedIn developer application, request organization publishing permission and set redirect URI.
- [ ] Create/configure Meta application and eligible Instagram Professional account; obtain correct publishing permissions.
- [ ] Configure HTTPS domain and secure OIDC admin sign-in.
- [ ] Implement state/PKCE callback, provider account selection, token encryption and disconnect.
- [ ] Replace in-memory data with PostgreSQL and durable approval audit.
- [ ] Implement approval UI and content calendar.
- [ ] Implement provider-specific media publishing and safe retry logic.
- [ ] Test revoked tokens, rejected posts, modified approved posts, cross-account access, duplicate jobs and scheduled revocation.
- [ ] Perform owner-authorized test posts only after explicit per-post approval.
