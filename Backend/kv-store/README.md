# cel — A Lightweight Key-Value Store in C

`cel` is a memory-safe, TCP-based key-value store written in C. It's designed to act like a simplified version of Redis—perfect for learning systems-level programming, handling real-time caching, and solving scalability issues in multi-process environments like Node.js apps.

---

## 🚀 Features

- 🧠 In-memory key-value storage
- 🔌 TCP socket server (custom protocol)
- ✅ Supports `SET`, `GET`, and `DELETE` commands
- 🛡️ Safe buffer handling and input validation
- 🛠️ Easily extendable for persistence, TTL, and more

---

## 🧪 Example Usage

Once the server is running:

```bash
./kvstore

