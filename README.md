# Secure Graph Exchange Protocol

This document outlines the communication and cryptography protocol used to securely transmit graph datasets between the Data Owner (Node A) and the Model Trainer (Node B).

## Protocol Sequence Diagram

```text
Node A (Data Owner)                                Node B (Model Trainer)
       |                                                      |
       |  [Out-of-band: Exchange Public Keys]                 |
       |                                                      |
       | 1. Generate Symmetric Session Key (AES)              |
       | 2. Encrypt Session Key with Node B's Public Key      |
       |----------------------------------------------------->| (Send Encrypted Session Key)
       |                                                      |
       | 3. Hash Graph Data (SHA-256 for Integrity)           |
       | 4. Sign Graph Data with Node A's Private Key (Auth)  |
       | 5. Package Graph Data, Hash, and Signature           |
       | 6. Encrypt Payload with Symmetric Session Key        |
       |----------------------------------------------------->| (Send Encrypted Payload)
       |                                                      |
       |                                                      | 7. Decrypt Session Key using Node B's Private Key
       |                                                      | 8. Decrypt Payload using Session Key
       |                                                      | 9. Verify Hash matches Data (Integrity check)
       |                                                      | 10. Verify Signature using Node A's Public Key
       |                                                      | 11. Load & Visualize Graph Dataset
       |                                (Connection Closes)   |
       |------------------------------------------------------|
```

## Security Guarantees
1. **Confidentiality:** Handled via Hybrid Encryption. The large graph data is encrypted with a fast symmetric key (AES via Fernet), and the symmetric key is encrypted using RSA public-key cryptography.
2. **Integrity:** Handled via SHA-256 hashing. If a Man-In-The-Middle (MITM) alters the payload, the recalculation of the hash on Node B will fail.
3. **Authentication & Non-repudiation:** Handled via RSA Digital Signatures. Only Node A holds the private key capable of generating the signature that Node B verifies using Node A's public key.
