# BrandGuard — Intelligent Pre-Publication Brand Governance

[![CodeTitans India 2026](https://img.shields.io/badge/CodeTitans%20India%202026-Round%202%20Build-blue)](https://wecodecoders.in/events/codetitans-india)
[![Problem Statement](https://img.shields.io/badge/Problem%20Statement-Inkloom%20AI-purple)](https://wecodecoders.in/events/codetitans-india)
[![Status](https://img.shields.io/badge/Status-Round%202%20Shipped%20%26%20Verified-emerald)]()
[![Accuracy Benchmark](https://img.shields.io/badge/Validation%20Accuracy-90.0%25-brightgreen)]()

> **Team Name:** WHO CARES?  
> **Team Members:** Peehu (Leader & Backend Lead), Rhythm Uppal (Frontend & UX Lead), Saatvik Bardwaj (AI Review Engine Lead), Prabashish Singh (Testing & Delivery Lead)  
> **Problem Statement:** Inkloom AI: Intelligent brand-governance platform that reviews content *before* it is published.

---

## 🎯 Executive Summary & Round 2 Objective

In Round 1, Team **WHO CARES?** designed the blueprint for BrandGuard to solve a ubiquitous enterprise crisis: employees, agencies, and generative AI tools publish marketing copy, legal notices, and press releases that contain unverified claims, expired discounts, offensive slang, and brand identity violations before anyone notices.

In **Round 2 (The Build)**, we transformed the proposal into a working, functional product that judges and users can run and verify from beginning to end:
1. **Content Ingestion:** Type copy, paste text/markdown, or upload Word (`.docx`) or PDF documents.
2. **Deterministic & Heuristic 4-Layer Inspection:** Terminology, Claims & Expired Facts, Tone & Voice, and Numbered Guideline Citations.
3. **Interactive Tracked Changes Diff Engine:** Red strikethrough for deletions, green highlight for approved replacements, with one-click Accept, Edit, or Reject.
4. **Human Decision & Sign-Off Pipeline:** Enforces human oversight (`Draft` → `Auto-Checked` → `In Review` → `Approved`).
5. **Immutable Cryptographic Audit Trail:** Logs every check, suggestion action, comment, and signoff with SHA-256 hashes.
6. **Empirical Accuracy Test Suite:** 30-item validation benchmark showing **90.0% Detection Accuracy** and **100% Rule Citation Coverage** at **0.13 ms latency**.

---

## 🚀 Quick Start (One Command to Run)

BrandGuard uses a unified single-port architecture: the FastAPI backend serves both the interactive React frontend SPA and all REST endpoints directly on `http://127.0.0.1:8000/`.

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ (only needed if modifying frontend assets)

### Launch
```bash
# Clone the repository
git clone <YOUR_REPO_URL>
cd BrandGuard_Project

# Run the unified server
python run.py
```
Open **`http://127.0.0.1:8000/`** in any web browser (including private/incognito mode — **no login required**).

---

## 🧭 Live Demo Walkthrough for Judges (10-Second Test)

1. Open **`http://127.0.0.1:8000/`**.
2. Click any of the **Preloaded Test Scenarios** in the top bar:
   - **`⚡ Marketing Launch Social Post`**: Triggers unverified claim `#1 in India`, expired Black Friday discount, banned word `cheap`, and casual slang `bro`.
   - **`⚠️ Bereavement Notice`**: Triggers Air Canada chatbot precedent violations (`unlimited refund` promise, casual `lol` acronym, wrong customer terminology).
   - **`✅ Compliant Release`**: Demonstrates a 100% compliant post with verified facts (`FACT-01`) and green consistency score.
3. Observe the **Brand Consistency Scorecard** and category breakdown.
4. Review the **Interactive Tracked Changes Diff**:
   - Click **"Accept & Apply Fix"** on any suggestion. Watch the content update in real-time and the brand score rise!
   - Click **"Reject / Dismiss"** on a critical finding — enter a justification (feeds the Guideline Health engine).
5. Use the **Human Governance Bar**:
   - Switch role to **Brand Manager** or **Legal Reviewer** in the top-right role switcher.
   - Click **"Grant Final Brand Approval"** to trigger celebratory confetti and lock the document status to `Approved`.
6. Click the **"Accuracy Benchmark"** tab in the navigation header to run the live 30-item validation test suite in real time!

---

## 🏗️ System Architecture

```
                                 [ User Interface ]
                       React 18 + Vite + Lucide + Diff Engine
                                         │
                                         ▼ (REST / JSON)
                                 [ FastAPI Router ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
 [ File Extractors ]           [ 4-Layer Rule Engine ]          [ Workflow & Audit ]
 • PyMuPDF (PDF)               • Layer 1: Terminology Regex     • State Machine
 • python-docx (Word)          • Layer 2: Fact Register Match   • Version History
 • Plain Text / Markdown       • Layer 3: Tone & Voice Rules    • SHA-256 Audit Logs
                               • Layer 4: Rule Citation Engine
                                         │
                                         ▼
                               [ SQLite Storage (WAL) ]
                      • Guidelines  • Facts Register  • Audit Logs
```

---

## 📊 Completed Round 2 Features

| Feature Module | Shipped Capability |
| :--- | :--- |
| **Brand Knowledge Base** | Stores guidelines, banned terms with replacements, preferred terms, and an Approved Facts Register with active dates, sources, and expiration flags. Includes live in-UI CRUD to register custom facts and terms. |
| **Multi-Format Ingestion** | Ingests pasted copy, `.docx` Word documents, and `.pdf` files via PyMuPDF and python-docx without third-party services. |
| **Source-Cited Findings** | Every finding names its exact rule ID (e.g. `RULE-CLAIM-01`), citation source, and confidence score. Zero unsourced flags. |
| **Interactive Policy Inspector** | Dual-mode editor: switch between raw text editing and a visual inspector highlighting policy infractions with glowing inline badges and rule tooltips. |
| **Tracked Changes Engine** | Character/word-level diff viewer showing deletions and additions with 1-click **"Magic Fix All"**, Accept, Edit, or Reject. |
| **Dual Clearance Exports** | Generates an official signed 1-page PDF Brand Clearance Certificate and a formatted publication-ready Microsoft Word (`.docx`) document. |
| **Rejection Feedback** | Requires justifications when dismissing critical flags, feeding the self-healing guideline engine. |
| **Human Sign-Off Bar** | Enforces human approval (`Draft` → `Auto-Checked` → `In Review` → `Approved`) with instant role switcher and celebratory confetti. |
| **Cryptographic Audit Log** | Immutable log tracking timestamp, actor, role, event type, and SHA-256 content hashes. |
| **Validation Benchmark** | In-app runner testing 30 hidden-mistake cases, measuring detection rate (90.0%) and latency (0.13ms). |

---

## 🔄 Explanation of Changes Made to the Original Plan

1. **Unified Single-Port Deployment:**  
   *Original Plan:* Separate frontend and backend ports (`localhost:5173` and `localhost:8000`).  
   *Actual Build:* Unified into FastAPI static mounts. The SPA and API are served together on port 8000. This ensures zero CORS friction and frictionless evaluation by judges in private/incognito windows.
2. **Front-Loaded Validation Benchmark from Round 3:**  
   *Original Plan:* Test set of 30 items was planned for Round 3 testing.  
   *Actual Build:* Delivered in Round 2. We embedded an interactive benchmark runner directly into the product UI so judges can test empirical accuracy (90.0%) and latency (0.13ms) with one click.
3. **Base64 Document Streaming:**  
   *Original Plan:* Multipart form uploads.  
   *Actual Build:* Transitioned to Base64 JSON streaming to eliminate server-side multipart dependency bugs and enable instant client-side preview before transmission.

---

## 🌟 Three Major Improvements Committed for Round 3

As required by CodeTitans India 2026, we commit to three meaningful functional improvements for Round 3:

### 1. Multimodal Visual & Accessibility Compliance Engine
- **Scope:** Extends BrandGuard beyond text to analyze image assets, banner ads, and graphic collateral.
- **Capabilities:**
  - Automated brand color palette extraction and HEX deviation distance calculation (Delta E < 2.0).
  - Logo aspect-ratio, safe-space padding, and distortion detection using OpenCV.
  - Automated WCAG 2.1 AA/AAA text-to-background contrast ratio validation across rendered graphics.
  - AI-assisted image alt-text generation and accessibility certification.

### 2. Enterprise Privacy Shield & Local AI Inference Pipeline
- **Scope:** Air-gapped and high-confidentiality operational mode for unreleased PR and financial disclosures.
- **Capabilities:**
  - Automated PII and confidential entity masking before external API egress.
  - Zero-data-retention guarantee with local quantized model toggle (ONNX/Ollama).
  - Immutable cryptographic AI Disclosure Ledger tracking prompt parameters, models, and tokens.
  - 100% deterministic local rules kill-switch.

### 3. Continuous Guideline Health & Self-Healing Governance Insights
- **Scope:** Transforms brand governance from a static rulebook into an adaptive, self-optimizing learning loop.
- **Capabilities:**
  - Statistical dispute analysis flagging ambiguous rules that creators/reviewers frequently dismiss or override.
  - Conflicting guideline and contradictory fact detection across disparate policy documents.
  - AI-suggested guideline rewrites recommending simpler, clearer rule definitions to brand administrators.
  - Team-level velocity metrics measuring time-to-approval and repeat violation trends.

---

## 👥 Team & Individual Contributions

| Member | Round 2 Module Owned & Delivered | Proof of Work |
| :--- | :--- | :--- |
| **Peehu** (Leader, Backend Lead) | Core FastAPI architecture, SQLite database schema, review & approval state transitions, version snapshots, and cryptographic audit logging. | Backend codebase, database persistence, and API documentation. |
| **Rhythm Uppal** (Frontend & UX Lead) | High-fidelity SaaS interface, interactive Tracked Changes Diff Engine, live Scorecard, Brand Knowledge Hub, and Accuracy Benchmark screens. | React components, CSS3 design system, and user interaction flow. |
| **Saatvik Bardwaj** (AI Review Engine Lead) | 4-layer rule inspection engine, Approved Facts Register, expiry logic, and source citation engine ensuring 100% of findings name approved rules. | Rule engine algorithms, fact-matching logic, and test cases. |
| **Prabashish Singh** (Testing & Delivery Lead) | 30-item validation test dataset, PyMuPDF/python-docx multi-format extractors, automated benchmark verification, and Docker packaging. | Benchmark test suite, file extractors, and Round 2 PDF submission. |

---

## 📄 Submission Files

- **Working Project Link:** Accessible locally at `http://127.0.0.1:8000/` (or deployed URL).
- **Updated Project PDF:** `BrandGuard_Round2_Submission.pdf` (generated and stored in repository root).
- **Source Code Repository:** GitHub repository with clean commit history.
