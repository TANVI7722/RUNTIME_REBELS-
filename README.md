# SYNVARA — Intelligent Operational Monitoring & Local Edge AI for Primary Healthcare

[![GitHub Repo](https://img.shields.io/badge/GitHub-RUNTIME__REBELS-181717?style=flat&logo=github)](https://github.com/TANVI7722/RUNTIME_REBELS)
[![Edge AI](https://img.shields.io/badge/Edge%20AI-Isolation%20Forest%20%2B%20FaceNet-0d9488)](https://github.com/TANVI7722/RUNTIME_REBELS)
[![Offline First](https://img.shields.io/badge/Architecture-100%25%20Offline%20First-0284c7)](https://github.com/TANVI7722/RUNTIME_REBELS)
[![IPHS 2022](https://img.shields.io/badge/Compliance-IPHS%202022%20Continuity-16a34a)](https://github.com/TANVI7722/RUNTIME_REBELS)
[![DPDP Act 2023](https://img.shields.io/badge/Audit-DPDP%20Act%202023%20SHA--256-7c3aed)](https://github.com/TANVI7722/RUNTIME_REBELS)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Repository:** [https://github.com/TANVI7722/RUNTIME_REBELS](https://github.com/TANVI7722/RUNTIME_REBELS)  
> **Developed by:** **Team RUNTIME REBELS**

---

## 📌 Executive Summary

**SYNVARA** is an offline-first Edge AI operational resilience framework engineered for rural Primary Health Centres (PHCs). Peripheral healthcare clinics routinely experience prolonged internet blackouts and erratic power, causing cloud-based attendance and biometric portals to fail. This leads to administrative blindspots, unannounced staff absenteeism, phantom muster roll records, and paralyzed emergency and maternal delivery wards.

SYNVARA solves this by migrating biometric authentication, operational anomaly detection, and clinical service contingency directly to the local edge node.

---

## ⚡ Core Pillars & Capabilities

### 1. On-Device Edge Face Biometrics & Liveness
* Complete facial recognition and anti-spoof micro-liveness verification executed on-device.
* Zero raw biometric templates are leaked across public networks; runs in **< 240ms** local latency.

### 2. IPHS 2022 Clinical Service Continuity Engine
* Real-time monitoring of 4 critical PHC wings:
  1. **Emergency & Trauma Stabilization**
  2. **Maternity & 24x7 Labour Room**
  3. **General Outpatient (OPD)**
  4. **Pharmacy & Cold-Chain Logistics**
* If scheduled medical officers are absent or delayed, the engine automatically checks qualifications and prompts pre-approved relief staff from the **IPHS 15% reserve pool**.

### 3. Isolation Forest Anomaly Detection AI
* Unsupervised machine learning models run on-device to detect proxy attendance, abnormal sign-in times, and anomalous absenteeism clusters.

### 4. Cryptographic Append-Only Audit Ledger
* Fully compliant with India's **Digital Personal Data Protection Act 2023 (DPDP Act 2023)**.
* Attendance logs and supervisory modifications are immutably chained using **SHA-256 cryptographic hashes**. Original records can never be overwritten or erased.

### 5. Opportunistic P2P Mesh & Cloud Synchronization
* Audits are cached locally in SQLite and IndexedDB. Once connectivity is restored, queued batches synchronize automatically with District Command.

### 6. Grassroots Trilingual Interface
* Native language switcher supporting **English (EN)**, **Marathi (मराठी - MR)**, and **Hindi (हिन्दी - HI)** tailored for rural auxiliary nurses (ANMs) and clinic staff.

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

## 🏛️ Multi-Tier Persona Architecture

1. **🩺 Medical Officer (Dr. Rajesh Kulkarni):** In-charge clinical overview, service availability ratios, alert triage, and emergency replacement authorizations.
2. **👩‍⚕️ PHC Staff Nurse (Nurse Sunita Patil):** Simplified single-purpose view: daily shift hours, instant biometric check-in, and leave entitlement balance.
3. **🏛️ District Health Officer (Dr. V. G. Shinde):** 360° district fleet surveillance across all peripheral PHC nodes (Shirwal, Bhor, Velhe, Khandala) with cross-facility reallocation.
4. **💻 System Administrator (Admin S. Pawar):** Edge device telemetry, node sync latency, AI threshold calibration, and DPDP Act audit ledger export.

---

## 🚀 Getting Started & Local Setup

### Prerequisites
* Python 3.10 or higher
* Node.js & npm *(optional)*

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TANVI7722/RUNTIME_REBELS.git
   cd RUNTIME_REBELS
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn scikit-learn numpy opencv-python pydantic
   ```

3. **Start the SYNVARA Edge Server:**
   ```bash
   python server.py
   ```

4. **Access the Portal:**
   * **Landing Page:** [http://localhost:8000/#landing](http://localhost:8000/#landing)
   * **Login Gateway:** [http://localhost:8000/#login](http://localhost:8000/#login)
   * **Operations Portal:** [http://localhost:8000/#app](http://localhost:8000/#app)
   * **FastAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👥 Team: RUNTIME REBELS

* **GitHub:** [https://github.com/TANVI7722/RUNTIME_REBELS](https://github.com/TANVI7722/RUNTIME_REBELS)
* **Organization:** PCCOE
* **Project:** SYNVARA — Intelligent Operational Monitoring for Primary Healthcare
