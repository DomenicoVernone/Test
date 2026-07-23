# API Security Summary — Clinical Twin
**Project:** Tesi-FTD — MLOps Clinical Twin  
**Standard:** OWASP API Security Top 10 (2023)  
**Date:** 2026-06-23

---

## Introduction

This security documentation is organized into three files. The **Code Changes** file (`security_code_changes.md`) describes in detail the 30 implemented changes, divided into 6 thematic groups (JWT authentication, authorization, input validation, resource protection, configuration, and secure features added): each change includes the code before and after the fix, an explanation of the attack it prevents, and its concrete impact. The **Tests** file (`security_tests.md`) collects the 10 manual tests run with PowerShell to verify that the protections actually work at runtime, with ready-to-use commands, expected output, and obtained results. This summary file provides a quick overview: the table of all 30 changes, the OWASP security score per category, and the two measures not yet implemented.

---

## Summary Table of All 30 Changes

| #  | Change | Main File | OWASP |
|----|--------|-----------|-------|
| 1  | Access token expiry set to 15 minutes | `api_gateway/core/config.py:11` | API2 |
| 2  | Refresh token in httpOnly + SameSite=Strict cookie | `api_gateway/routers/auth.py:38-47` | API2 |
| 3  | JTI blacklist on logout (token revocation) | `api_gateway/core/security.py:87-138` | API2 |
| 4  | SECRET_KEY >= 64 characters (validator) | `api_gateway/core/config.py:24-31` | API2 |
| 5  | JWT `sub` = numeric user_id (RFC 7519) | `api_gateway/core/security.py:62-66` | API2 |
| 6  | Explicit bcrypt rounds=12 (auditable) | `api_gateway/core/security.py:17-21` | API2 |
| 7  | Timing attack protection (dummy hash) | `api_gateway/core/security.py:28,39-48` | API2 |
| 8  | Password strength validation (8+/upper/digit) | `api_gateway/models/schemas.py:20-29` | API2 |
| 9  | BOLA: owner_id filter on every task query | `orchestrator/routers/analyze.py:120-178` | API1 |
| 10 | BFLA: UserRole enum user/admin | `api_gateway/models/domain.py:7-23` | API5 |
| 11 | Centralized `require_admin` dependency | `api_gateway/core/security.py:120-126` | API5 |
| 12 | Segregated `/admin/*` endpoints | `auth.py:238-258`, `analyze.py:192-203` | API5 |
| 13 | Mass assignment: separate input/output schemas | `api_gateway/models/schemas.py:6-54` | API3 |
| 14 | model_name whitelist — no SSRF/path traversal | `orchestrator/routers/analyze.py:20-29` | API7 |
| 15 | Username regex whitelist — XSS prevention | `api_gateway/models/schemas.py:11-18` | API3 |
| 16 | NIfTI file validation with magic bytes | `orchestrator/routers/analyze.py:32-66` | API3 |
| 17 | Login rate limiting: 5/minute | `api_gateway/routers/auth.py:100` | API4 |
| 18 | Registration rate limiting: 3/min (admin), 5/h (public) | `api_gateway/routers/auth.py:53,76` | API4 |
| 19 | MRI analysis pipeline rate limiting: 3/minute | `orchestrator/routers/analyze.py:70` | API4 |
| 20 | Forgot-password rate limiting: 3/hour | `api_gateway/routers/auth.py:186` | API4 |
| 21 | HTTP security headers on all microservices | `*/main.py:SecurityHeadersMiddleware` | API8 |
| 22 | Swagger/OpenAPI docs hidden in production | `api_gateway/main.py:90-98` | API9 |
| 23 | Microservice ports bound to loopback 127.0.0.1 | `docker-compose.yml:27,46,65,88,109` | API8 |
| 24 | R errors not exposed to client (generic message) | `model_service/main.py:75-83` | API8 |
| 25 | MLflow fallback with generic error | `model_service/main.py:86-94` | API10 |
| 26 | Public registration `/register` — fixed role `user` | `api_gateway/routers/auth.py:75-94` | API5 |
| 27 | `/forgot-password` — always returns 200 | `api_gateway/routers/auth.py:185-205` | API2 |
| 28 | `/reset-password` — single-use token with expiry | `api_gateway/routers/auth.py:208-233` | API2 |
| 29 | SMTP credentials from environment variables (.env) | `api_gateway/services/email.py` | API8 |
| 30 | Invalidation of previous reset tokens (rotation) | `api_gateway/routers/auth.py:193-200` | API2 |

---

## OWASP Security Score

| OWASP | Category | Score | Notes |
|-------|----------|-------|-------|
| API1  | Broken Object Level Authorization | ✅ | BOLA with `owner_id` on all task queries (#9) |
| API2  | Broken Authentication | ✅ | 8 changes: JWT 15min, httpOnly cookie, JTI blacklist, bcrypt 12, timing, password strength, forgot/reset secure (#1–8, #27–28, #30) |
| API3  | Broken Object Property Level Auth | ✅ | Separate schemas, username regex, NIfTI magic bytes (#13, #15, #16) |
| API4  | Unrestricted Resource Consumption | ✅ | Rate limiting on login, register, pipeline, forgot-password (#17–20) |
| API5  | Broken Function Level Authorization | ✅ | Role enum, require_admin, /admin/* endpoints segregated, secure register (#10–12, #26) |
| API6  | Unrestricted Access to Sensitive Flows | ⚠️ | Rate limiting present; native authentication on the R inference engine is missing (access only via internal Docker network) |
| API7  | Server Side Request Forgery | ✅ | model_name whitelist on both orchestrator and model_service (#14) |
| API8  | Security Misconfiguration | ✅ | Security headers, hidden docs, loopback binding, generic errors, credentials from env (#21–24, #29) |
| API9  | Improper Inventory Management | ✅ | Swagger/OpenAPI docs disabled in production (#22) |
| API10 | Unsafe Consumption of APIs | ✅ | MLflow fallback with generic error and internal logging (#25) |

**Legend:**
- ✅ Covered with effective, code-verified measures
- ⚠️ Partially covered — present but with room for improvement
- ❌ Not covered

**Overall score: 9/10 categories covered (API6 partial)**

---

## Changes Not Implemented

The following measures were indicated in the project specification but **are not implemented** in the analysed code:

### 1. JWT revocation after password reset

**Status:** ❌ Not implemented  
**Where missing:** `api_gateway/routers/auth.py:208-233` (function `reset_password`)  
**Problem:** After a password reset, active session JWTs are NOT revoked. An attacker who already holds a valid access token (stolen before the reset) can continue using it for the remaining 15 minutes.  
**Recommended fix:** Add a `password_changed_at` field to the `User` model and verify in `get_current_user()` that the JWT was issued after that timestamp. Alternatively, revoke all active JWTs for the user by inserting their JTIs into the blacklist at reset time.

```python
# To add in reset_password() after user.hashed_password = ...
user.password_changed_at = datetime.now(timezone.utc)
db.commit()

# To add in get_current_user() after token decode:
if user.password_changed_at:
    token_iat = datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc)
    if token_iat < user.password_changed_at:
        raise HTTPException(status_code=401, detail="Token invalid after password change")
```

### 2. Client-side lockout after failed attempts (60 seconds)

**Status:** ⚠️ Not verifiable from backend code  
**Where it should be:** React frontend code (not analysed)  
**Note:** This logic resides in the frontend and cannot be verified from backend code analysis. Note that a client-side lockout is **UX only** — it can be bypassed by any tool that is not the browser. The server-side rate limiting (#17) is the real protection and is correctly implemented.

---

*Summary generated on 2026-06-23 — Static analysis on 13 source files*  
*Standard: OWASP API Security Top 10 (2023 Edition)*
