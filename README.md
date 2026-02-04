🛡️ FraudGuard

Agentic Honeypot System for Scam Detection & Intelligence Extraction

FraudGuard is an agent-driven honeypot system that actively engages scam conversations, detects malicious intent, extracts intelligence, and reports verified scam data through a controlled callback mechanism.

The system is designed for predictability, safety, and control, even when AI components are involved.

🚨 What Problem FraudGuard Solves

Scam communications today are:

adaptive and conversational

resistant to static rules

designed to extract sensitive information quickly

FraudGuard flips the problem by:

engaging scammers instead of blocking them

collecting intelligence without alerting the attacker

terminating conversations safely

reporting only verified results

🧠 How FraudGuard Works (In One View)
Incoming Message
      ↓
  Decision Engine
      ↓
  Agentic Engagement
      ↓
Intelligence Extraction
      ↓
 Safe Termination
      ↓
 Verified Callback


Each step is controlled, state-aware, and non-aggressive.

🧩 Core Capabilities

🧠 Scam intent detection

🤖 Human-like agent responses

🔍 Passive intelligence extraction (UPI, links, numbers)

🔁 State-driven conversation flow

📤 Single, verified callback reporting

🏗️ Project Structure
contracts/      # Interface definitions
receiver/       # Input validation & normalization
decision/       # Scam detection & state transitions
aiagent/        # Controlled conversational agent
extraction/     # Intelligence extraction
callback/       # Final reporting
orchestrator/   # System control flow


Each module has one responsibility and operates independently.

🔁 Execution Model

Every session exists in one runtime state

Only one component controls flow

No module acts independently

No uncontrolled loops

This prevents:

false positives

infinite engagement

accidental exposure

🧪 Current Status

✅ System design completed

✅ Interfaces defined

🔄 Implementation in progress

🔒 Design Guarantee

FraudGuard is built to ensure that:

AI never controls the system

decisions are explicit

exits are safe

reporting happens exactly once

Final Note

FraudGuard does not chase scammers.
It controls them