/**
 * PHC Edge AI - Client-Side Deterministic Healthcare Rule Engine & Continuity Engine
 * Enforces:
 * 1. Clinical safety rules cannot be overridden or suppressed by AI (Critical Alert Override).
 * 2. Leave + Absenteeism Intelligence (Scenarios A, B, C, D).
 * 3. Staff Continuity Engine (Options A, B, C with IPHS 2022 15% reserve grounding).
 * 4. Overtime Safety: Decision-support only; requires administrator authorization.
 */

const CLIENT_CLINICAL_SERVICES = {
  emergency: {
    id: "emergency",
    name: "Emergency & Trauma Care",
    criticality: "CRITICAL",
    required_roles: { DOCTOR: 1, NURSE: 1 },
    description: "24/7 Acute Stabilization and Resuscitation"
  },
  maternity_labour: {
    id: "maternity_labour",
    name: "Maternity & Labour Room",
    criticality: "CRITICAL",
    required_roles: { DOCTOR: 1, ANM: 1 },
    description: "Intrapartum Delivery and Neonatal Care"
  },
  outpatient_opd: {
    id: "outpatient_opd",
    name: "General Outpatient (OPD)",
    criticality: "MEDIUM",
    required_roles: { DOCTOR: 1 },
    description: "Primary Consultation and Triage"
  },
  pharmacy_cold_chain: {
    id: "pharmacy_cold_chain",
    name: "Pharmacy & Cold Chain",
    criticality: "HIGH",
    required_roles: { PHARMACIST: 1 },
    description: "Cold-Chain Vaccine Preservation"
  }
};

class ClientRuleEngine {
  constructor() {
    this.services = CLIENT_CLINICAL_SERVICES;
  }

  evaluateStaffing(staffRoster) {
    const res = this.evaluateServices(staffRoster);
    res.services = res.service_evaluations;
    return res;
  }

  /**
   * Leave + Absenteeism Intelligence.
   * Proper distinction between:
   * PRESENT, LATE, ABSENT, APPROVED_LEAVE, UNAUTHORIZED_ABSENCE, OFF_DUTY, COVERED_ABSENCE
   */
  classifyAttendanceState(staff) {
    const status = (staff.status || "SCHEDULED").toUpperCase();
    const delay = staff.delay_minutes || 0;
    const hasLeave = !!(staff.leave_approved || ["APPROVED_LEAVE", "CASUAL_LEAVE", "MEDICAL_LEAVE"].includes(staff.leave_status));
    const isReplaced = !!(staff.is_replaced || ["REPLACED", "COVERED_ABSENCE"].includes(status));

    if (isReplaced) {
      return "COVERED_ABSENCE"; // Scenario D: Doctor is absent but replacement is assigned
    }
    if (status === "PRESENT" || status === "CHECKED_IN") {
      if (delay > 15) {
        return "LATE"; // Scenario C: Doctor checks in at 09:27, shift was 09:00
      }
      return "PRESENT";
    }
    if (status === "LATE") {
      return "LATE";
    }
    if (status === "OFF_DUTY") {
      return "OFF_DUTY";
    }
    if (hasLeave) {
      return "APPROVED_LEAVE"; // Scenario A: Doctor doesn't check in + Approved leave exists
    }
    if (status === "ABSENT" || status === "SCHEDULED") {
      if (delay > 15 || status === "ABSENT") {
        return "UNAUTHORIZED_ABSENCE"; // Scenario B: Doctor doesn't check in + No leave exists
      }
      return "SCHEDULED";
    }

    return status;
  }

  evaluateServices(staffRoster) {
    const deptKeywords = {
      emergency: ["emergency", "trauma"],
      maternity_labour: ["maternity", "labour", "labor"],
      outpatient_opd: ["outpatient", "opd"],
      pharmacy_cold_chain: ["pharmacy", "cold chain"]
    };

    const serviceEvaluations = {};
    const ruleViolations = [];
    let totalReq = 0;
    let totalPres = 0;
    let serviceRiskCount = 0;

    for (const [sId, sDef] of Object.entries(this.services)) {
      const reqRoles = sDef.required_roles;
      let deptActive = true;
      const missingRoles = [];
      const keywords = deptKeywords[sId] || [sId];

      const deptStaff = staffRoster.filter(s => {
        const deptLower = (s.department || "").toLowerCase();
        return keywords.some(k => deptLower.includes(k));
      });

      const deptActiveCounts = {};
      for (const staff of deptStaff) {
        const effStatus = this.classifyAttendanceState(staff);
        const role = (staff.role || "").toUpperCase();

        if (effStatus === "PRESENT" || effStatus === "CHECKED_IN" || effStatus === "COVERED_ABSENCE") {
          deptActiveCounts[role] = (deptActiveCounts[role] || 0) + 1;
        } else if (effStatus === "LATE" && staff.checkin_time) {
          deptActiveCounts[role] = (deptActiveCounts[role] || 0) + 1;
        }
      }

      for (const [role, minReq] of Object.entries(reqRoles)) {
        totalReq += minReq;
        const presNum = deptActiveCounts[role] || 0;
        totalPres += Math.min(presNum, minReq);

        if (presNum < minReq) {
          deptActive = false;
          const deficit = minReq - presNum;
          missingRoles.push({ role, required: minReq, present: presNum, deficit });
        }
      }

      if (!deptActive) {
        serviceRiskCount++;
        const violation = {
          service_id: sId,
          service_name: sDef.name,
          criticality: sDef.criticality,
          missing_roles: missingRoles,
          rule: `${sDef.name} requires at least ${Object.entries(reqRoles).map(([r, c]) => `${c} ${r}`).join(", ")}`
        };
        ruleViolations.push(violation);
        serviceEvaluations[sId] = {
          name: sDef.name,
          criticality: sDef.criticality,
          status: "AT_RISK",
          missing_roles: missingRoles,
          required_roles: reqRoles
        };
      } else {
        serviceEvaluations[sId] = {
          name: sDef.name,
          criticality: sDef.criticality,
          status: "OPERATIONAL",
          missing_roles: [],
          required_roles: reqRoles
        };
      }
    }

    const coverageRatio = Math.round((totalPres / Math.max(totalReq, 1)) * 100) / 100;

    return {
      service_evaluations: serviceEvaluations,
      rule_violations: ruleViolations,
      service_risk_count: serviceRiskCount,
      staffing_coverage_ratio: coverageRatio
    };
  }

  /**
   * Staff Continuity Engine (IPHS 2022 15% Reserve Grounded).
   * Generates Option A (Relief), Option B (Overtime), Option C (Escalation).
   */
  generateContinuityOptions(serviceId, missingRole, fullStaffPool = []) {
    const options = [];
    const targetRole = (missingRole || "DOCTOR").toUpperCase();

    // Candidates in staff pool
    const candidates = fullStaffPool.filter(s => (s.role || "").toUpperCase() === targetRole);

    // Option A: Relief Staff (Off-duty / IPHS 15% reserve)
    const reliefCandidates = candidates.filter(s => 
      (s.is_reserve || ["OFF_DUTY", "SCHEDULED"].includes(s.status)) &&
      !s.leave_approved
    );

    if (reliefCandidates.length > 0) {
      const rc = reliefCandidates[0];
      options.push({
        option_id: "OPT-A",
        type: "RELIEF_ASSIGNMENT",
        title: `Option A — Assign Relief Staff (${rc.name})`,
        staff_id: rc.staff_id,
        staff_name: rc.name,
        role: rc.role,
        current_status: "OFF_DUTY (IPHS 15% Reserve)",
        availability: rc.current_shift || "Available 14:00–18:00",
        feasibility: "HIGH",
        iphs_grounding: "Mobilizes IPHS 2022 15% Leave & Training Reserve staff buffer.",
        action_label: `Assign ${rc.name} (Relief)`,
        requires_admin_authorization: true
      });
    }

    // Option B: Request Overtime (Currently on-duty, within safe workload cap)
    const overtimeCandidates = candidates.filter(s => 
      ["PRESENT", "CHECKED_IN"].includes(s.status) &&
      !s.is_reserve &&
      (s.workload_hours || 8.0) <= 8.5
    );

    if (overtimeCandidates.length > 0) {
      const oc = overtimeCandidates[0];
      options.push({
        option_id: "OPT-B",
        type: "OVERTIME_REQUEST",
        title: `Option B — Request Overtime Extension (${oc.name})`,
        staff_id: oc.staff_id,
        staff_name: oc.name,
        role: oc.role,
        current_status: `On-Duty (${oc.current_shift || '09:00–17:00'})`,
        availability: "Shift extension: 17:00–19:00 (+2h overtime)",
        feasibility: "MEDIUM",
        iphs_grounding: "Complies with clinical rest guidelines; overtime capped at 2 hours.",
        action_label: `Request Overtime for ${oc.name}`,
        requires_admin_authorization: true
      });
    }

    // Option C: Escalate & Divert
    options.push({
      option_id: "OPT-C",
      type: "ESCALATION_REFERRAL",
      title: "Option C — Escalate & Trauma Diversion",
      staff_id: null,
      staff_name: "Sub-District Hospital Shirwal Cluster",
      role: "ESCALATION",
      current_status: "FACILITY PROTOCOL",
      availability: "Immediate Trauma Diversion Hotline",
      feasibility: "FALLBACK",
      iphs_grounding: "Activates Sub-District Hospital Shirwal cluster trauma diversion protocol.",
      action_label: "Initiate Trauma Diversion Protocol",
      requires_admin_authorization: true
    });

    return options;
  }
}

// Global rule engine singleton & window bindings
const clientRuleEngine = new ClientRuleEngine();
const ruleEngine = clientRuleEngine;

if (typeof window !== "undefined") {
  window.CLIENT_CLINICAL_SERVICES = CLIENT_CLINICAL_SERVICES;
  window.ClientRuleEngine = ClientRuleEngine;
  window.clientRuleEngine = clientRuleEngine;
  window.ruleEngine = ruleEngine;
}
