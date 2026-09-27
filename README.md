# SYNVARA

### Smart PHC Workforce & Service Availability Intelligence Platform

> **From attendance data to actionable healthcare operations.**

SYNVARA is a digital operations platform designed to help district health administrators monitor whether **Primary Health Centres (PHCs) and subcentres are actually capable of delivering their planned healthcare services**.

Instead of treating every missing attendance record as an absence, SYNVARA brings together **staff schedules, attendance, approved leave, service availability and synchronization status** to identify genuine operational gaps and help administrators resolve them.

---

## 🎯 Problem

A PHC may have a planned staff roster and a defined set of healthcare services, but district administrators often lack a unified view of whether those services are actually available at a given time.

A missing attendance record could mean:

* A staff member is genuinely absent.
* The staff member is on approved leave.
* The employee arrived late.
* The PHC has not submitted its report yet.
* The facility is temporarily offline.
* The attendance system failed to synchronize.

Treating all of these situations as the same creates **false alerts and poor operational decisions**.

### The key question SYNVARA answers:

> **“Is this PHC actually capable of providing its planned services right now — and if not, why?”**

---

# 💡 Our Solution

SYNVARA connects four major operational data sources:

```text
Staff Schedule
      │
      ├──────────────┐
      ↓              ↓
Attendance       Approved Leave
      │              │
      └──────┬───────┘
             ↓
      Service Mapping
             │
             ↓
     Service Impact Engine
             │
             ↓
       Alert Classification
             │
             ↓
    Administrator Dashboard
             │
       ┌─────┴─────┐
       ↓           ↓
   Resolution    Audit Trail
```

The platform converts raw workforce and service information into an **actionable operational picture of each PHC**.

---

# 🚀 Core USP

## Attendance ≠ Service Availability

SYNVARA does not stop at asking:

> **“Is the employee present?”**

It asks:

> **“What healthcare service is affected if this employee is unavailable?”**

For example:

```text
Medical Officer
      ↓
Absent
      ↓
No approved leave
      ↓
Genuine staffing gap
      ↓
OPD affected
      ↓
HIGH IMPACT ALERT
      ↓
Administrator action
```

This creates a complete chain:

### **Attendance → Service Impact → Action**

---

# ⭐ Key Features

## 1. PHC & Subcentre Management

Maintain operational profiles for healthcare facilities.

* Facility profile
* Location
* Operating hours
* Available services
* Assigned workforce
* Service requirements
* Facility operational status

---

## 2. Staff Management

Maintain staff assignments and service responsibilities.

Example:

| Staff Role      | Assigned Service |
| --------------- | ---------------- |
| Medical Officer | OPD              |
| ANM             | Immunization     |
| Lab Technician  | Diagnostics      |
| Staff Nurse     | Maternal Care    |

This allows SYNVARA to understand the relationship between **staff availability and service availability**.

---

## 3. Attendance Monitoring

Simulated or integrated check-ins can be recorded for facility staff.

Possible states:

* Present
* Late
* Absent
* Pending
* Not reported

Attendance timestamps are maintained to support operational monitoring.

---

## 4. Approved Leave Detection

SYNVARA cross-checks attendance with approved leave.

### Example

```text
No Check-in
     ↓
Approved Leave Found
     ↓
Not treated as staffing failure
```

This prevents unnecessary alerts.

---

## 5. Intelligent Alert Classification

The system distinguishes between different operational situations.

### 🔴 Possible Staffing Gap

Staff expected to report but no attendance or approved leave is available.

### 🟡 Late Report

The facility has not submitted its expected update within the configured reporting window.

### 🟢 Approved Absence

Staff member is officially on approved leave.

### 🟠 Pending Synchronization

Data exists locally but has not yet reached the central system.

This prevents **missing data from automatically becoming a negative operational signal**.

---

# 🏥 Service Impact Engine

The central intelligence layer of SYNVARA.

Instead of simply reporting:

> **“Medical Officer absent.”**

the platform determines:

> **“Medical Officer absent → OPD service may be affected.”**

Example:

```text
PHC-021

Medical Officer       🔴 Absent
ANM                    🟢 Present
Staff Nurse            🟢 Present
Lab Technician         🟢 Present

--------------------------------

OPD                    🔴 At Risk
Immunization           🟢 Available
Maternal Care          🟢 Available
Diagnostics            🟢 Available

Overall Status:
PARTIALLY OPERATIONAL
```

---

# 📊 PHC Operational Status

SYNVARA provides a facility-level operational view.

### 🟢 Operational

Planned essential services are available.

### 🟡 Partially Operational

One or more services are affected but the facility continues to provide other services.

### 🔴 Critical Service Gap

An essential service is unavailable or significantly impacted.

The status is based on **service availability and operational context**, not attendance alone.

---

# 🚨 Administrator Alert Centre

Administrators can view active operational issues from a centralized dashboard.

Each alert provides:

* Facility
* Staff involved
* Expected attendance
* Actual attendance
* Leave status
* Affected service
* Severity
* Detection time
* Synchronization status
* Resolution status

---

# ✅ Alert Resolution

SYNVARA is designed around:

> **Alert → Investigate → Resolve → Record**

Example:

```text
Alert:
Medical Officer missing check-in

        ↓

Check approved leave

        ↓

No approved leave

        ↓

Verify facility status

        ↓

Assign backup staff

        ↓

Resolve alert

        ↓

Store resolution in audit trail
```

Administrators can record actions such as:

* Verified approved leave
* Confirmed late arrival
* Contacted facility
* Assigned backup staff
* Attendance/device issue
* Connectivity issue
* Other administrative action

---

# 📡 Offline-Tolerant Design

Rural healthcare facilities may experience unreliable connectivity.

SYNVARA therefore supports a mock delayed-sync workflow.

```text
PHC
 │
 │ Internet unavailable
 ↓
Local Data Storage
 │
 ↓
Pending Sync Queue
 │
 │ Connectivity restored
 ↓
Central Synchronization
 │
 ↓
Administrator Dashboard
```

The system records synchronization timestamps so that administrators can distinguish:

> **“No data received”**

from:

> **“Data received late because the facility was offline.”**

---

# 🔄 Delayed-Sync Scenario

Example:

```text
09:00
Expected check-in

09:05
PHC goes offline

09:10
Attendance recorded locally

09:30
Still offline

10:02
Connectivity restored

10:03
Data synchronized

10:03
Central dashboard updated
```

This prevents premature classification of the staff member as absent.

---

# 🧠 Intelligence Layer

SYNVARA can use a combination of:

### Rule-based operational intelligence

For deterministic situations such as:

```text
No check-in
+
No approved leave
=
Possible staffing gap
```

and:

```text
No recent update
+
Facility offline
=
Pending synchronization
```

### Service dependency analysis

Maps staff roles to services and identifies affected services when workforce availability changes.

### Future Analytics

The architecture can be extended to support:

* Repeated staffing-gap detection
* Recurring reporting delays
* Facility-level trends
* Service disruption patterns
* Workforce utilization analytics
* Predictive staffing-risk analysis

---

# 🧪  MVP

The current MVP focuses on the complete operational workflow:

### 1. Facility Management

Create and manage PHCs and their services.

### 2. Staff Management

Assign staff to facilities and services.

### 3. Attendance

Record simulated staff check-ins.

### 4. Leave

Record approved staff leave.

### 5. Service Mapping

Map required staff roles to healthcare services.

### 6. Alert Engine

Detect and classify operational gaps.

### 7. Service Impact

Determine which services are affected.

### 8. Administrator Dashboard

View facility and district-level operational status.

### 9. Alert Resolution

Allow administrators to investigate and resolve alerts.

### 10. Offline Simulation

Demonstrate delayed synchronization.

---

# 🎬 Demonstration Scenarios

## Scenario 1 — Genuine Staffing Gap

```text
Medical Officer expected
        ↓
No check-in
        ↓
No approved leave
        ↓
Staffing gap detected
        ↓
OPD marked at risk
        ↓
Administrator notified
        ↓
Resolution recorded
```

---

## Scenario 2 — Approved Leave

```text
Medical Officer absent
        ↓
Approved leave exists
        ↓
Absence classified correctly
        ↓
No false staffing-gap alert
```

---

## Scenario 3 — Late Report

```text
Expected facility update
        ↓
No report received
        ↓
Reporting window exceeded
        ↓
Late-report alert
        ↓
Not automatically classified as staff absence
```

---

## Scenario 4 — Offline Facility

```text
PHC loses connectivity
        ↓
Attendance stored locally
        ↓
Pending Sync
        ↓
Connectivity restored
        ↓
Data synchronized
        ↓
Dashboard updated
```

---

# 🏗️ System Architecture

```text
                    ┌───────────────────────┐
                    │    PHC / Subcentre    │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ↓                 ↓                 ↓
       Staff Schedule       Attendance        Service Data
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ↓
                       ┌─────────────────┐
                       │ Data Validation │
                       └────────┬────────┘
                                ↓
                    ┌────────────────────────┐
                    │ Service Impact Engine  │
                    └────────────┬───────────┘
                                 ↓
                    ┌────────────────────────┐
                    │   Alert Classification │
                    └────────────┬───────────┘
                                 ↓
                    ┌────────────────────────┐
                    │ Administrator Dashboard│
                    └────────────┬───────────┘
                                 ↓
                  ┌──────────────┴──────────────┐
                  ↓                             ↓
             Resolution                    Audit Trail
```

---

# 🛠️ Technology Stack

> Replace or update this section according to the technologies actually used in the implementation.

### Frontend

* React
* Vite
* HTML5
* CSS3
* JavaScript

### Backend

* Python
* FastAPI / REST API

### Database

* PostgreSQL / MySQL / SQLite

### Analytics

* Python
* Rule-based Service Impact Engine
* Optional ML/analytics modules

### Development

* Git
* GitHub
* REST APIs

---

# 📁 Repository Structure

```text
SYNVARA/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── requirements.txt
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── data/
│   └── synthetic/
│
├── docs/
│   ├── architecture/
│   ├── diagrams/
│   └── screenshots/
│
├── demo/
│   └── demo-scenarios.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

# 🔐 Data Privacy & Security

SYNVARA's hackathon implementation uses **synthetic/demo data**.

No real patient medical records, personally identifiable health information, authentication secrets, API keys or production credentials should be committed to this repository.

Production deployment should incorporate:

* Role-based access control
* Authentication
* Authorization
* Encryption in transit
* Encryption at rest
* Audit logging
* Secure API endpoints
* Data retention policies
* Appropriate healthcare data governance

---

# 🌐 Future Scope

SYNVARA can evolve into a broader PHC operations intelligence platform.

### Potential integrations

* Government health-information systems
* Existing attendance systems
* Facility registries
* Mobile-based PHC applications
* SMS/notification systems
* IoT-enabled facility monitoring

### Advanced analytics

* Staffing demand forecasting
* Recurring service-gap detection
* Facility performance trends
* Workforce optimization
* Early warning for persistent service disruptions

### Geographic Intelligence

District administrators could visualize:

```text
District
   ↓
Block
   ↓
PHC
   ↓
Service
   ↓
Current operational status
```

allowing resource allocation to be based on operational need.

---

# 🎯 Why SYNVARA?

Healthcare facility data often exists in different operational silos.

SYNVARA focuses on connecting these signals into one actionable view:

```text
                 SYNVARA
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Workforce   Attendance    Services
       │            │            │
       └────────────┼────────────┘
                    ↓
             Operational
             Intelligence
                    ↓
             Service Impact
                    ↓
              Admin Action
```

### Our core principle:

> **Don't just report what happened. Help identify what it means for service delivery and what action can be taken.**

---

# 👥 Team

**Project:** SYNVARA
**Problem Statement:** HLTH04 — PHC Staffing & Service-Availability Monitoring
**Hackathon:** HackMatrix

---

# 📌 Disclaimer

SYNVARA is a hackathon prototype developed to demonstrate the concept of integrated PHC workforce and service-availability monitoring.

The platform is not intended to replace existing government health-information systems or make autonomous clinical decisions.

---

