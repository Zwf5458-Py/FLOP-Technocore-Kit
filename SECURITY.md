# Security Policy

## 🔒 Security & Key Hygiene Policy

The **FLOP-Technocore-Kit** project is designed for developers exploring the FLOP Network and Technocore decentralized protocols. Because this project interacts with asymmetric cryptography (Ed25519) and Decentralized Identifiers (DIDs), strict cryptographic hygiene is paramount.

---

### 1. Zero-PrivateKey Leakage Guarantee

* **No Secrets Committed**: This repository enforces strict `.gitignore` filters prohibiting any `*.pem`, `*.key`, `*.passphrase`, `.agent_config.json`, or `.env*` credential files.
* **Separation of Keys**: Developers must **never** commit private identity files (`identity.pem`) or passphrases to version control.
* **Cold / Hot DID Isolation**: We strongly recommend using separate secondary DIDs for automated 24/7 cloud VPS bots, keeping the primary contributor DID secured in cold storage on local development workstations.

---

### 2. Supported Versions

| Version | Supported          | Security Status |
| :---    | :---               | :---            |
| 1.0.x   | :white_check_mark: | Active Security Maintenance |
| < 1.0   | :x:                | Deprecated / Not Supported |

---

### 3. Threat Model & Best Practices

1. **Passphrase Handling**:
   - Always load private key decryption passphrases via operating system environment variables (`TECHNOCORE_PASSPHRASE`) or interactive terminal prompts (`getpass.getpass()`).
   - Never hardcode passphrases in application scripts.
2. **Replay Attack Mitigation**:
   - Technocore signatures require strictly monotonic nonces. Always implement monotonic clocks or database-backed sequences to prevent signature replay or transaction reordering.
3. **Canonical Payloads**:
   - Technocore signing schemes require stripping of Unicode non-printable characters and canonical room formatting. Failure to normalize messages before signing can lead to message rejection.

---

### 4. Reporting a Security Vulnerability

If you discover a security vulnerability, an insecure default, or any potential flaw within this developer kit, please **do not open a public GitHub issue**.

Instead, report the issue responsibly:
* **Primary Contact**: Open an encrypted communication or report directly via Technocore DID:  
  `did:key:z6MkwBZMeaqfJpg3GPEd4jR719FxNZJmi2YURvxC9bgHozuT`
* **Email**: Contact the repository maintainer at the email address designated in git commit author metadata.

Please provide:
1. A description of the vulnerability and attack vector.
2. Reproducible proof-of-concept steps.
3. Potential mitigation or patch recommendations if available.

We will acknowledge receipt within 48 hours and work with you on a coordinated public disclosure.
