# gemini-cli-code-analysis

## ⚠️ SECURITY WARNING

This repository contains **INTENTIONALLY VULNERABLE CODE** for educational and demonstration purposes.

**DO NOT DEPLOY TO PRODUCTION OR PUBLICLY ACCESSIBLE SERVERS!**

## Purpose

This demo repository is designed to demonstrate:
- Gemini CLI code review capabilities
- Gemini CLI Security scanning and analysis tools

## Overview

This is a FastAPI-based Inventory Management System that has been intentionally modified to include OWASP security vulnerabilities:

1. Broken Access Control
2. Cryptographic Failures
3. Injection (SQL & Command)
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)

## Documentation

📖 **[Complete Security Vulnerabilities Documentation](SECURITY_VULNERABILITIES.md)**

See the detailed documentation for:
- Full list of vulnerabilities and affected endpoints
- Example exploits for each vulnerability type

## Running the Application

```bash
# Start the server
uv run main.py

# Or using uvicorn directly
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Full Endpoint List

See [SECURITY_VULNERABILITIES.md](SECURITY_VULNERABILITIES.md) for the complete list.

## Use Cases

❌ **NOT FOR PRODUCTION USE**  
❌ **DO NOT EXPOSE PUBLICLY**

## Responsible Disclosure

This code is intentionally vulnerable for educational purposes.

---

**Remember: This is vulnerable by design. Never use this code in production!**
