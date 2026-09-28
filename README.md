# SYNVARA

### Smart PHC Workforce & Service Availability Intelligence Platform
> **From attendance data to actionable healthcare operations.**

[![GitHub Repo](https://img.shields.io/badge/GitHub-RUNTIME__REBELS--181717?style=flat&logo=github)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![Edge AI](https://img.shields.io/badge/Edge%20AI-Isolation%20Forest%20%2B%20FaceNet-0d9488)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![Offline First](https://img.shields.io/badge/Architecture-100%25%20Offline%20First-0284c7)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![IPHS 2022](https://img.shields.io/badge/Compliance-IPHS%202022%20Continuity-16a34a)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![DPDP Act 2023](https://img.shields.io/badge/Audit-DPDP%20Act%202023%20SHA--256-7c3aed)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![Hackathon](https://img.shields.io/badge/Hackathon-HackMatrix-orange)](https://github.com/TANVI7722/RUNTIME_REBELS-)
[![Problem Statement](https://img.shields.io/badge/Problem%20Statement-HLTH04-blue)](https://github.com/TANVI7722/RUNTIME_REBELS-)

**Repository:** [https://github.com/TANVI7722/RUNTIME_REBELS-](https://github.com/TANVI7722/RUNTIME_REBELS-)  
**Team:** **RUNTIME REBELS** (PCCOE)  
**Problem Statement:** HLTH04 — PHC Staffing & Service-Availability Monitoring  
**Hackathon:** HackMatrix  

---

## 📌 Executive Summary

**SYNVARA** is a digital operations intelligence platform designed to help district health administrators and medical officers monitor whether **Primary Health Centres (PHCs) and subcentres are actually capable of delivering their planned healthcare services**.

Instead of treating every missing attendance record as an absence, SYNVARA fuses **staff schedules, on-device biometric attendance, approved leave, service requirements, and edge synchronization status** to identify genuine operational gaps and help administrators resolve them in real time.

---

## 🎯 The Problem

A PHC may have a planned staff roster and a defined set of healthcare services, but district administrators often lack a unified view of whether those services are actually operational.

A missing attendance record could mean:
* A staff member is genuinely absent.
* The staff member is on approved field/training leave.
* The employee arrived late.
* The PHC has not submitted its report yet.
* The facility is temporarily offline due to rural power or fiber cuts.
* The attendance system failed to synchronize.

Treating all of these situations identically creates **false alerts, administrative fatigue, and critical service blindspots**.

### The Key Question SYNVARA Answers:
> *"Is the clinic actually able to treat patients right now, and if not, who can cover the gap?"*

---

## ⚡ Core Capabilities & Implementation

### 1. On-Device Edge Face Biometrics & Liveness
* Complete facial recognition and anti-spoof micro-liveness verification running on-device.
* Zero raw biometric templates are sent to the cloud; sub-240ms verification latency.

### 2. IPHS 2022 Clinical Service Continuity Engine
* Real-time monitoring of 4 critical PHC wings:
  1. **Emergency & Trauma Stabilization**
  2. **Maternity & 24x7 Labour Room**
  3. **General Outpatient (OPD)**
  4. **Pharmacy & Cold-Chain Logistics**
* If scheduled medical officers are delayed or absent, the engine immediately suggests qualified relief staff from the **IPHS 15% reserve pool**.

### 3. Isolation Forest Anomaly Detection AI
* Unsupervised machine learning models run on-device to detect proxy attendance, abnormal sign-in times, and anomalous absenteeism clusters.

### 4. Cryptographic Append-Only Audit Ledger (DPDP Act 2023)
* Fully compliant with India's **Digital Personal Data Protection Act 2023**.
* Attendance logs and supervisory modifications are immutably chained using **SHA-256 cryptographic hashes**. Original records can never be overwritten or erased.

### 5. Opportunistic P2P Mesh & Cloud Synchronization
* Audits are cached locally in SQLite and IndexedDB. Once connectivity is restored, queued batches synchronize automatically with District Command.

### 6. Grassroots Trilingual Interface
* Native language switcher supporting **English (EN)**, **Marathi (मराठी - MR)**, and **Hindi (हिन्दी - HI)** tailored for rural auxiliary nurses (ANMs) and clinic staff.

---

## 🏗️ System Architecture

```text
                    ┌───────────────────────────┐
                    │  Rural PHC Hardware Node  │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ↓                        ↓                        ↓
  Staff Schedule         On-Device Face Net        IPHS Service Matrix
  (Doctor/Nurse)         (Haar & Cosine Sim)       (Emergency, Labour)
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │ Local Isolation Forest  │
                     │  Edge Anomaly Detection │
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │  Clinical Impact Engine │
                     │   (IPHS 2022 Continuity)│
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │ Append-Only Hash Ledger │
                     │   (SHA-256 / DPDP 2023) │
                     └────────────┬────────────┘
                                  ↓
                     ┌─────────────────────────┐
                     │ Opportunistic Mesh Sync │
                     └────────────┬────────────┘
                                  ↓
                    ┌───────────────────────────┐
                    │ District Fleet Dashboard  │
                    │    (DHO Fleet Command)    │
                    └───────────────────────────┘
```

---

## 🎬 Operational Scenarios

### Scenario 1 — Genuine Emergency Staffing Gap
```text
Emergency Doctor expected
        ↓
No biometric check-in within grace window
        ↓
No sanctioned leave in local database
        ↓
IPHS Contingency Alert: "Emergency Room At Risk"
        ↓
System recommends Dr. Rahul Mehra (IPHS Relief Pool)
        ↓
Medical Officer authorizes coverage with 1-click
```

### Scenario 2 — Approved Leave Coverage
```text
Staff Nurse absent
        ↓
Sanctioned leave record confirmed in audit ledger
        ↓
Absence classified as SANCTIONED_LEAVE
        ↓
No false alarm or penalty triggered
```

### Scenario 3 — Total Rural Internet Blackout
```text
Optical fiber disconnected (Offline Mode)
        ↓
Autonomous Edge AI continues on-device face check-ins
        ↓
Audit events written to local SQLite ledger
        ↓
Internet connectivity restores
        ↓
Opportunistic sync pushes verified batch to District Cloud
```

---

## 🛠️ Complete Tech Stack

| Layer | Technologies | Justification |
| :--- | :--- | :--- |
| **Edge AI & ML** | Scikit-Learn (Isolation Forest), OpenCV, NumPy | Low-overhead on-device facial recognition and anomaly detection. |
| **Frontend UI/UX** | HTML5, Vanilla CSS3, Modern ES6+ JS | Zero heavyweight third-party libraries; ultra-responsive glassmorphism on low-spec edge PCs. |
| **Offline Storage** | IndexedDB (Browser) + SQLite3 (Server Node) | 100% offline operational continuity during network failures. |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn | Async ASGI server delivering low-latency local endpoints and mesh synchronization. |
| **Security & Standards**| SHA-256 Chaining, DPDP Act 2023, IPHS 2022 | Statutory compliance, tamper resistance, and patient privacy. |

---

## 👥 Multi-Tier Persona Architecture

1. **🩺 Medical Officer (Dr. Rajesh Kulkarni):** In-charge clinical overview, service availability ratios, alert triage, and emergency replacement authorizations.
2. **👩‍⚕️ PHC Staff Nurse (Nurse Sunita Patil):** Simplified single-purpose view: daily shift hours, instant biometric check-in, and leave entitlement balance.
3. **🏛️ District Health Officer (Dr. V. G. Shinde):** 360° district fleet surveillance across all peripheral PHC nodes (Shirwal, Bhor, Velhe, Khandala) with cross-facility reallocation.
4. **💻 System Administrator (Admin S. Pawar):** Edge device telemetry, node sync latency, AI threshold calibration, and DPDP Act audit ledger export.

---

## 🚀 Getting Started & Local Setup

### Prerequisites
* Python 3.10 or higher

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TANVI7722/RUNTIME_REBELS-.git
   cd RUNTIME_REBELS-
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn scikit-learn numpy opencv-python pydantic
   ```

3. **Start the SYNVARA Edge Server:**
   ```bash
   python server.py
   ```

4. **Access the Portal in your browser:**
   * **Landing Page:** [http://localhost:8000/#landing](http://localhost:8000/#landing)
   * **Login Gateway:** [http://localhost:8000/#login](http://localhost:8000/#login)
   * **Operations Portal:** [http://localhost:8000/#app](http://localhost:8000/#app)
   * **FastAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 Team: RUNTIME REBELS

* **Repository:** [https://github.com/TANVI7722/RUNTIME_REBELS-](https://github.com/TANVI7722/RUNTIME_REBELS-)
* **Organization:** PCCOE
* **Problem Statement:** HLTH04 — PHC Staffing & Service-Availability Monitoring
* **Hackathon:** HackMatrix
* **License:** MIT
