<div align="center">

# 🛡️ FraudGuard
### Agentic Honeypot System for Scam Detection & Intelligence Extraction

![Python](https://img.shields.io/badge/Python-100%25-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-In%20Progress-orange?style=for-the-badge)

<p align="center">
  <b>FraudGuard</b> is an agent-driven honeypot system that actively engages scam conversations, detects malicious intent, extracts intelligence, and reports verified scam data through a controlled callback mechanism.
  <br><br>
  <i>Designed for predictability, safety, and control, even when AI components are involved.</i>
</p>

</div>

---

## 🚨 What Problem FraudGuard Solves

Scam communications today are **adaptive, conversational, and resistant to static rules**, often designed to extract sensitive information quickly.

**FraudGuard flips the problem by:**
* **Engaging** scammers instead of blocking them.
* **Collecting** intelligence without alerting the attacker.
* **Terminating** conversations safely.
* **Reporting** only verified results.

---

## 🧠 How FraudGuard Works

The system follows a strict, linear flow to ensure safety and control.

```mermaid
graph TD
    A[Incoming Message] --> B[Decision Engine]
    B --> C[Agentic Engagement]
    C --> D[Intelligence Extraction]
    D --> E[Safe Termination]
    E --> F[Verified Callback]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#9f9,stroke:#333,stroke-width:2px

## 🧩 Core Capabilities

| Feature | Description |
| --- | --- |
| **🧠 Intent Detection** | Accurately identifies scam intent versus normal conversation. |
| **🤖 Agent Responses** | Generates human-like, context-aware replies to keep scammers engaged. |
| **🔍 Passive Extraction** | Silently captures intelligence (UPI, links, phone numbers). |
| **🔁 State-Driven Flow** | Strictly manages the conversation lifecycle. |
| **📤 Verified Reporting** | Triggers a single, verified callback upon conclusion. |

---

## 🏗️ Project Structure

Each module has **one responsibility** and operates independently.

```bash
FraudGuard/
├── contracts/      # Interface definitions
├── receiver/       # Input validation & normalization
├── decision/       # Scam detection & state transitions
├── aiagent/        # Controlled conversational agent
├── extraction/     # Intelligence extraction
├── callback/       # Final reporting
└── orchestrator/   # System control flow

```

---

## 🔁 Execution Model

To ensure safety, FraudGuard enforces a strict execution model:

1. Every session exists in **one runtime state**.
2. **Only one component** controls flow at a time.
3. **No module** acts independently.
4. **No uncontrolled loops**.

> **Why?** This prevents false positives, infinite engagement loops, and accidental exposure.

---

## 🧪 Current Status

* [x] **System design completed**
* [x] **Interfaces defined**
* [ ] **Implementation in progress**

---

## 🔒 Design Guarantee

FraudGuard is built on a "Safety First" architecture:

> 1. **AI never controls the system.**
> 2. **Decisions are explicit.**
> 3. **Exits are safe.**
> 4. **Reporting happens exactly once.**
> 
> 

<div align="center">





<h3><i>"FraudGuard does not chase scammers. It controls them."</i></h3>
</div>

```

```