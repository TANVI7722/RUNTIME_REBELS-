/**
 * PHC Edge AI - 09:00 to 09:31 Emergency Continuity Interactive Scenario Simulator
 * Walkthrough demonstrating:
 * OFFLINE -> LOCAL RULES -> EDGE AI -> CONTINUITY RECOMMENDATION -> ADMIN APPROVAL -> AUDIT SYNC
 */

const SCENARIO_STEPS = [
  {
    step: 1,
    time: "09:00",
    title: "Doctor Scheduled",
    category: "NORMAL_OPERATION",
    summary: "Dr. Rajesh Kulkarni scheduled on duty for 24/7 Emergency & Trauma Care.",
    details: "Shift starts at PHC Shirwal. Nurse Sunita Patil checked in (08:52) via Edge Face AI. Emergency Care requirement is 1 Doctor + 1 Nurse. Central cloud connection is active. All services operational.",
    isOffline: false,
    staffUpdate: { "STF-001": { status: "SCHEDULED", checkin_time: null, delay_minutes: 0, is_replaced: false } },
    expectedScore: 0.15,
    expectedState: "NORMAL",
    actionsNeeded: null
  },
  {
    step: 2,
    time: "09:10",
    title: "Doctor Missing",
    category: "OPERATIONAL_GAP",
    summary: "10 minutes past shift start. Emergency Doctor has not arrived or checked in.",
    details: "Medical Officer Dr. Rajesh Kulkarni is overdue. System checks: Approved leave exists? NO -> Flagged as UNEXPLAINED DELAY (Scenario B candidate). Staff presence shows Doctor = MISSING, Nurse = PRESENT.",
    isOffline: false,
    staffUpdate: { "STF-001": { status: "LATE", checkin_time: null, delay_minutes: 10, is_replaced: false } },
    expectedScore: 0.58,
    expectedState: "ELEVATED",
    actionsNeeded: null
  },
  {
    step: 3,
    time: "09:12",
    title: "Internet Disconnected",
    category: "OFFLINE_EVENT",
    summary: "Rural fiber optic link severed. Internet connectivity drops to 0 kbps.",
    details: "PHC loses connection to central district cloud server. System automatically switches to EDGE AUTONOMOUS MODE. Local Edge AI Models (Face AI + Anomaly Detector) and Rule Engine remain 100% operational.",
    isOffline: true,
    staffUpdate: null,
    expectedScore: 0.64,
    expectedState: "ELEVATED",
    actionsNeeded: null
  },
  {
    step: 4,
    time: "09:15",
    title: "Edge AI Detects Pattern",
    category: "EDGE_INFERENCE",
    summary: "Edge AI Isolation Forest runs local inference without internet.",
    details: "Edge AI Model 2 detects sharp operational deviation: Staffing coverage dropped to 62% (vs 88% baseline). 15 mins average check-in delay. Offline pending queue rising. Anomaly score calculated locally at 0.86 (UNUSUAL).",
    isOffline: true,
    staffUpdate: { "STF-001": { status: "UNAUTHORIZED_ABSENCE", checkin_time: null, delay_minutes: 15, is_replaced: false } },
    expectedScore: 0.86,
    expectedState: "UNUSUAL",
    actionsNeeded: null
  },
  {
    step: 5,
    time: "09:16",
    title: "Local Rule Engine Evaluates",
    category: "RULE_EVALUATION",
    summary: "Deterministic safety rules evaluate: Emergency Care AT RISK.",
    details: "Rule Engine: Emergency Care requires min 1 Doctor + 1 Nurse. Available Doctor = 0. Rule condition: IF emergency_required > available THEN service_status = AT_RISK. System asks: 'How can the service continue?'",
    isOffline: true,
    staffUpdate: null,
    expectedScore: 0.86,
    expectedState: "UNUSUAL",
    actionsNeeded: null
  },
  {
    step: 6,
    title: "Continuity Options Generated",
    category: "ALERT_FUSION",
    summary: "Alert Fusion merges Rule Engine + Edge AI -> CRITICAL ALERT & Continuity Options.",
    details: "CRITICAL ALERT OVERRIDE active: Safety violation forces CRITICAL priority. Staff Continuity Engine calculates 3 coverage options: Option A (Assign Relief Dr. Rahul from 15% IPHS reserve), Option B (Request Overtime), Option C (Trauma Diversion). Requires Admin authorization.",
    isOffline: true,
    staffUpdate: null,
    expectedScore: 0.86,
    expectedState: "UNUSUAL",
    actionsNeeded: "CONTINUITY_PROMPT"
  },
  {
    step: 7,
    time: "09:17",
    title: "Admin Authorizes Relief Staff",
    category: "EMERGENCY_CONTINUITY",
    summary: "Admin authorizes Option A: Dr. Rahul Mehra mobilized from IPHS 15% Reserve.",
    details: "Medical Officer In-Charge authorizes Option A (Dr. Rahul Mehra, Relief MO, Available). Dr. Rajesh Kulkarni absence marked as COVERED ABSENCE (Scenario D). Immutable event REPLACEMENT_ASSIGNED appended to local ledger. Emergency care restored.",
    isOffline: true,
    staffUpdate: {
      "STF-001": { status: "COVERED_ABSENCE", is_replaced: true, note: "Covered by Relief MO Dr. Rahul Mehra" },
      "STF-007": { status: "PRESENT", checkin_time: "09:17" }
    },
    expectedScore: 0.42,
    expectedState: "NORMAL",
    actionsNeeded: null
  },
  {
    step: 8,
    time: "09:30",
    title: "Internet Restored",
    category: "ONLINE_EVENT",
    summary: "Connectivity restored. Edge node detects central cloud heartbeat.",
    details: "Network uplink active. Edge node verifies pending queue: 1 Critical Alert, 1 Continuity Plan, 1 Immutable Attendance Event, 2 Edge AI Inferences. Auto-sync handshake initiated.",
    isOffline: false,
    staffUpdate: null,
    expectedScore: 0.28,
    expectedState: "NORMAL",
    actionsNeeded: null
  },
  {
    step: 9,
    time: "09:31",
    title: "Priority Batch Sync",
    category: "CLOUD_SYNC",
    summary: "IndexedDB queue uploads with priority ordering and deduplication.",
    details: "CRITICAL Alert & Continuity Authorization uploaded FIRST, followed by Immutable Attendance Events with cryptographic hashes, then Edge AI Inferences. Central cloud confirms receipt with 0 duplicate conflicts.",
    isOffline: false,
    staffUpdate: null,
    expectedScore: 0.18,
    expectedState: "NORMAL",
    actionsNeeded: null
  },
  {
    step: 10,
    time: "09:31",
    title: "District Audit Verified",
    category: "AUDIT_COMPLETE",
    summary: "District Health Officer views complete unbroken incident & continuity timeline.",
    details: "Central Command Center reflects exact sequence: Outage, Edge AI detection, safety rule trigger, IPHS 15% reserve mobilization, administrator authorization, and unbroken cryptographic event ledger.",
    isOffline: false,
    staffUpdate: null,
    expectedScore: 0.15,
    expectedState: "NORMAL",
    actionsNeeded: null
  }
];

class ScenarioPlayer {
  constructor(app) {
    this.app = app;
    this.steps = SCENARIO_STEPS;
    this.currentStepIndex = 0;
    this.isPlaying = false;
    this.timer = null;
  }

  getCurrentStep() {
    return this.steps[this.currentStepIndex];
  }

  async setStep(stepIndex) {
    if (stepIndex < 0 || stepIndex >= this.steps.length) return;
    this.currentStepIndex = stepIndex;
    const step = this.steps[this.currentStepIndex];

    await this.applyStepState(step);
    this.render();
  }

  async nextStep() {
    if (this.currentStepIndex < this.steps.length - 1) {
      await this.setStep(this.currentStepIndex + 1);
    } else {
      this.pause();
    }
  }

  async prevStep() {
    if (this.currentStepIndex > 0) {
      await this.setStep(this.currentStepIndex - 1);
    }
  }

  async play() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.renderControls();

    const loop = async () => {
      if (!this.isPlaying) return;
      if (this.currentStepIndex < this.steps.length - 1) {
        await this.nextStep();
        this.timer = setTimeout(loop, 4500);
      } else {
        this.pause();
      }
    };
    this.timer = setTimeout(loop, 3000);
  }

  pause() {
    this.isPlaying = false;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.renderControls();
  }

  async reset() {
    this.pause();
    this.currentStepIndex = 0;
    await this.setStep(0);
  }

  async applyStepState(step) {
    if (this.app) {
      this.app.setConnectivity(!step.isOffline);
    }

    if (step.staffUpdate && this.app && this.app.roster) {
      for (const [stfId, upd] of Object.entries(step.staffUpdate)) {
        let staff = this.app.roster.find(s => s.staff_id === stfId);
        if (staff) {
          Object.assign(staff, upd);
        } else if (this.app.fullStaffPool) {
          const poolStaff = this.app.fullStaffPool.find(s => s.staff_id === stfId);
          if (poolStaff) {
            const copy = Object.assign({}, poolStaff, upd);
            this.app.roster.push(copy);
          }
        }
      }
    }

    if (this.app) {
      await this.app.evaluateCurrentState(step.expectedScore);
    }

    // Save event record
    const eventRecord = {
      event_id: `EV-${Date.now()}-${step.step}`,
      facility_id: "PHC-004",
      timestamp: `2026-09-26T${step.time}:00`,
      event_type: step.category,
      payload: {
        step: step.step,
        title: step.title,
        summary: step.summary,
        offline: step.isOffline
      },
      priority: step.step === 6 ? "CRITICAL" : "NORMAL",
      sync_status: step.isOffline ? "PENDING" : "SYNCED"
    };
    await edgeStorage.saveEvent(eventRecord);

    if (step.step === 7) {
      // Append REPLACEMENT_ASSIGNED to ledger
      const attRecord = {
        event_id: `ATT-EV-RELIEF-${Date.now() % 100000}`,
        facility_id: "PHC-004",
        staff_id: "STF-007",
        staff_name: "Dr. Rahul Mehra",
        timestamp: new Date().toISOString(),
        event_type: "REPLACEMENT_ASSIGNED",
        status_code: "COVERED_ABSENCE",
        device_id: "ADMIN-CONSOLE",
        verification_method: "MANUAL_AUTHORIZED",
        proxy_risk_score: 0.0,
        proxy_risk_level: "LOW",
        created_by: "Medical Superintendent",
        sync_status: step.isOffline ? "PENDING" : "SYNCED",
        previous_event_id: "ATT-EV-PREV",
        event_hash: "H-RELIEF-" + Math.floor(Math.random() * 90000 + 10000),
        notes: "Authorized Option A: Dr. Rahul Mehra assigned to Emergency Care from IPHS 15% Reserve Pool."
      };
      await edgeStorage.saveAttendanceEvent(attRecord);
    }

    if (step.step === 9) {
      await syncClient.triggerSync("PHC-004");
    }
  }

  render() {
    this.renderTimeline();
    this.renderDetail();
    this.renderControls();
  }

  renderTimeline() {
    const nodes = document.querySelectorAll(".step-node");
    nodes.forEach((node, idx) => {
      node.classList.toggle("active", idx === this.currentStepIndex);
      node.classList.toggle("passed", idx < this.currentStepIndex);
    });

    const progressBar = document.getElementById("scenario-progress-bar");
    if (progressBar && this.steps.length > 1) {
      const pct = (this.currentStepIndex / (this.steps.length - 1)) * 100;
      progressBar.style.width = `${pct}%`;
    }
  }

  renderDetail() {
    const detailBox = document.getElementById("scenario-step-detail");
    if (!detailBox) return;

    const step = this.getCurrentStep();
    const isOff = step.isOffline;

    detailBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.8rem;">
        <div>
          <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #0284c7; letter-spacing: 0.05em;">
            Step ${step.step} of ${this.steps.length} • Timestamp: ${step.time}
          </span>
          <h3 style="font-size: 1.25rem; font-weight: 800; color: var(--text-main); margin-top: 0.2rem;">
            ${step.title}
          </h3>
        </div>
        <div style="display: flex; gap: 0.4rem; align-items: center;">
          <span class="badge ${isOff ? 'badge-offline' : 'badge-online'}">
            ${isOff ? 'OFFLINE MODE' : 'CLOUD CONNECTED'}
          </span>
          <span class="badge" style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd;">
            AI Score: ${step.expectedScore.toFixed(2)} (${step.expectedState})
          </span>
        </div>
      </div>

      <div style="background: #faf6ee; padding: 1rem; border-radius: 8px; border: 1px solid var(--border-subtle); border-left: 4px solid ${isOff ? '#b45309' : '#0284c7'}; margin-bottom: 1rem;">
        <strong style="color: var(--text-main); font-size: 0.95rem;">${step.summary}</strong>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.4rem; line-height: 1.5;">
          ${step.details}
        </p>
      </div>

      ${step.step === 6 ? `
        <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.8rem;">
          <div style="font-size: 0.78rem; font-weight: 700; color: #b91c1c; text-transform: uppercase;">
            Continuity Engine Recommendation Active:
          </div>
          <div style="font-size: 0.85rem; color: #991b1b; margin-top: 0.2rem;">
            Emergency Care missing 1 Doctor. System recommends: <strong>Option A (Dr. Rahul Mehra - IPHS 15% Reserve)</strong>. Advance to Step 7 to see Administrator authorization in action.
          </div>
        </div>
      ` : ''}

      <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-dim);">
        <span>Category: <code>${step.category}</code></span>
        <span>IPHS 2022 Continuity Protocol Guided</span>
      </div>
    `;
  }

  renderControls() {
    const playBtn = document.getElementById("scenario-btn-play");
    if (playBtn) {
      playBtn.textContent = this.isPlaying ? "Pause" : "Auto Play";
      playBtn.classList.toggle("btn-warning", this.isPlaying);
      playBtn.classList.toggle("btn-primary", !this.isPlaying);
    }
  }
}
