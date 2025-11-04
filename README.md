# Gemini CLI Code Analysis Demo

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
6. Software and Data Integrity Failures
7. Security Logging and Monitoring Failures
8. Server-Side Request Forgery (SSRF)

## How to run the Gemini CLI demo

1. Change branch to `refactor/analysis-demo`

    ```bash
    git checkout refactor/analysis-demo
    ```

2. Creating GEMINI.md for code review best practices

    ```bash
    gemini --yolo --output-format text "create a comprehensive best practice on code review guideline for reviewers and write to GEMINI.md"
    ```

3.  Run the code-review process

    ```bash
    gemini --yolo --output-format text "/code-review" > code-review.md
    ```

4. Run the security scanning process

    ```bash
    gemini --yolo --output-format text "/security:analyze" > security-analysis.md
    ```

5. Inspect the result on `code-review.md` and `security-analysis.md`

## Use Cases

❌ **NOT FOR PRODUCTION USE**  
❌ **DO NOT EXPOSE PUBLICLY**

## Responsible Disclosure

This code is intentionally vulnerable for educational purposes.

---

**Remember: This is vulnerable by design. Never use this code in production!**
