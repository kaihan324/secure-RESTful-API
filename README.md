
# Secure Data Storage RESTful API

This project is a practical assignment for an Information Security / Cryptography course. The goal is to design and implement a **RESTful API** that can:
1. register and authenticate users securely,
2. store users’ sensitive data **encrypted**,
3. manage cryptographic keys in a secure way,
4. and issue **JWT** tokens for accessing protected endpoints. :contentReference[oaicite:2]{index=2}

The focus is on **confidentiality**, **integrity**, and **secure key management**.

---

## Features

- **User registration**: users can create an account with username and password. Passwords are **never stored in plain text** and must be hashed (e.g. with **SHA-512**) before saving to the database. A unique **salt** and an application-level **pepper** must be used. :contentReference[oaicite:3]{index=3}
- **User login**: after successful authentication, the API issues a **JWT** that the client can use for all subsequent requests. :contentReference[oaicite:4]{index=4}
- **Secure storage of sensitive data**: users can send sensitive information (card number, address, personal info, …) and the API **encrypts** it (e.g. with **AES**) before saving it to the database (**encryption at rest**). :contentReference[oaicite:5]{index=5}
- **Secure retrieval**: only authenticated users can retrieve their encrypted records; the API decrypts the data on demand and returns it in plaintext. :contentReference[oaicite:6]{index=6}
- **Token expiration & security controls**: JWTs must have an expiration time; login attempts should be limited to mitigate **brute-force** attacks. :contentReference[oaicite:7]{index=7}
- **Optional KMS (extra points)**: a separate key management module/service to generate, store, and rotate encryption keys; can be implemented using an external tool like **HashiCorp Vault** or **Keycloak**, or a custom secure storage. The main idea is that if the database is leaked, the data is still protected. :contentReference[oaicite:8]{index=8}

---

## API Endpoints (Suggested)

> Note: exact routes can vary; below is a typical structure that satisfies the assignment.

### 1. Auth
- `POST /auth/register`  
  - Body: `{ "username": "...", "password": "..." }`  
  - Actions:
    - hash password with SHA-512
    - apply **salt** (per-user) and **pepper** (global)
    - store user in DB  
  - Returns: `201 Created`

- `POST /auth/login`  
  - Body: `{ "username": "...", "password": "..." }`  
  - Actions:
    - verify password (hashing again with same salt+pepper)
    - if OK → issue **JWT** with expiration
  - Returns: `{ "access_token": "<JWT_TOKEN>" }`  
  - Security: limit failed attempts. :contentReference[oaicite:9]{index=9}

### 2. Sensitive Data
- `POST /data` (protected)
  - Headers: `Authorization: Bearer <JWT>`
  - Body: `{ "type": "card|address|note", "value": "..." }`
  - Actions:
    - fetch encryption key from KMS / key store
    - encrypt value (e.g. AES-GCM / AES-CBC + HMAC)
    - store encrypted value in DB with user_id
  - Returns: stored object id

- `GET /data` (protected)
  - Returns list of user’s encrypted items (or decrypted, depending on design)
  - If encrypted in DB → API decrypts **on the fly** before sending. :contentReference[oaicite:10]{index=10}

- `GET /data/{id}` (protected)
  - Returns decrypted value belonging to that user.

---

## Security Design

- **Password handling**:  
  - Hash algorithm: `SHA-512` (or better: PBKDF2/Bcrypt/Argon2 if allowed)  
  - Add **per-user salt** and store it alongside the user  
  - Add **global pepper** in app config / env (not in DB)  
  - Store only the **hash** in DB, never the raw password. :contentReference[oaicite:11]{index=11}

- **JWT**:
  - issued on login
  - short lifetime (e.g. 15–60 minutes)
  - must be verified on every protected endpoint
  - expired tokens must be rejected. :contentReference[oaicite:12]{index=12}

- **Encryption**:
  - Symmetric encryption (e.g. AES) for sensitive fields
  - Keys must be stored **outside** normal tables or protected by KMS
  - Decryption happens only when the **authenticated** user calls GET. :contentReference[oaicite:13]{index=13}

- **Key Management (KMS)** (optional / bonus):  
  - a service / module to:
    - generate keys
    - store keys in an encrypted storage
    - fetch the right key per user / per record
  - idea: even if DB is dumped, encrypted data remains safe because keys are not there. :contentReference[oaicite:14]{index=14}

---

## Tech Stack (Flexible)

The assignment allows **any server-side language** that supports RESTful API development (Node.js, Python, Java, .NET, Go, …) and **any database** (MySQL, PostgreSQL, MongoDB, …). DB schema design is up to the student. API must be documented (Swagger or Postman collection). :contentReference[oaicite:15]{index=15}

---

## Documentation & Deliverables

The assignment requires:
- **Complete source code** runnable on a local machine
- **API documentation** (Swagger / Postman) with request/response examples
- **Technical report (max 2 pages)** describing:
  - system architecture
  - chosen crypto & hash algorithms
  - database structure
  - key management approach
  - and reasons for the choices
- **Demo video (~5 minutes)** showing:
  - project intro
  - folder structure
  - running the server & DB
  - calling the APIs (register, login, store, retrieve)
  - key management explanation. :contentReference[oaicite:16]{index=16}

---

## How to Run (example)

1. Clone the repo  
2. Configure DB connection + JWT secret + encryption key / KMS  
3. Install dependencies  
4. Run the API server  
5. Import Swagger/Postman and test endpoints

(Adjust this section to your actual language/framework.)

---

## Future Improvements

- per-user encryption keys
- key rotation & revocation
- audit log for sensitive operations
- 2FA on login
