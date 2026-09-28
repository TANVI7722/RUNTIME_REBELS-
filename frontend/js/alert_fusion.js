/**
 * PHC Edge AI - Alert Fusion & Clinical Explainability Synthesizer
 * Merges Deterministic Rules + Edge AI Anomaly Scores and enforces Critical Alert Override.
 * Integrates Staff Continuity Recommendations (Options A, B, C).
 */

class AlertFusionEngine {
  constructor() {}

  fuseAlerts(ruleResult, edgeAiResult, fullStaffPool = [], facilityId = "PHC-004", isOffline = false) {
    if (typeof fullStaffPool === "boolean") {
      isOffline = fullStaffPool;
      fullStaffPool = (typeof window !== "undefined" && window.app && window.app.fullStaffPool) ? window.app.fullStaffPool : [];
    }
    const fusedAlerts = [];
    const ruleViolations = (ruleResult && ruleResult.rule_violations) ? ruleResult.rule_violations : [];
    const aiScore = (edgeAiResult && typeof edgeAiResult.anomaly_score === "number") ? edgeAiResult.anomaly_score : 0.0;
    const aiStatus = (edgeAiResult && edgeAiResult.status) ? edgeAiResult.status : "NORMAL";
    const aiExplanation = (edgeAiResult && edgeAiResult.explanation) ? edgeAiResult.explanation : "";
    const factors = (edgeAiResult && edgeAiResult.top_contributing_factors) ? edgeAiResult.top_contributing_factors : [];

    // 1. Process deterministic safety rule violations
    for (const violation of ruleViolations) {
      const sName = violation.service_name;
      const crit = violation.criticality;
      const missingStr = violation.missing_roles.map(m => `${m.deficit} ${m.role}`).join(", ");

      let fusedPriority = "MEDIUM";
      let overrideActive = false;

      if (crit === "CRITICAL") {
        fusedPriority = "CRITICAL";
        // Critical Alert Override Principle:
        // If AI anomaly score is low (< 0.70), safety rule forces CRITICAL priority regardless!
        overrideActive = aiScore < 0.70;
      } else {
        fusedPriority = aiScore >= 0.75 ? "HIGH" : "MEDIUM";
      }

      // Synthesize fusion narrative
      const message = `${sName} is currently AT RISK because required staff (${missingStr}) is not checked in. ` +
        `Edge AI also detected operational state '${aiStatus}' (Anomaly Score: ${aiScore.toFixed(2)}). ` +
        `Local reasoning: ${aiExplanation}`;

      // Generate Staff Continuity Options (Options A, B, C)
      const firstMissingRole = violation.missing_roles[0]?.role || "DOCTOR";
      const continuityOptions = clientRuleEngine.generateContinuityOptions(
        violation.service_id,
        firstMissingRole,
        fullStaffPool
      );

      fusedAlerts.push({
        alert_id: `ALT-${facilityId}-${Math.floor(Date.now() % 100000)}`,
        timestamp: new Date().toISOString(),
        priority: fusedPriority,
        service_id: violation.service_id,
        service_name: sName,
        rule_violation: violation.rule,
        ai_anomaly_score: aiScore,
        ai_status: aiStatus,
        critical_override_active: overrideActive,
        offline_generated: isOffline,
        message: message,
        top_factors: factors.slice(0, 2),
        continuity_options: continuityOptions,
        status: "ACTIVE"
      });
    }

    // 2. If no rule violation, but Edge AI detected UNUSUAL or CRITICAL pattern
    if (ruleViolations.length === 0 && aiScore >= 0.75) {
      fusedAlerts.push({
        alert_id: `ALT-${facilityId}-ANOM-${Math.floor(Date.now() % 100000)}`,
        timestamp: new Date().toISOString(),
        priority: aiScore >= 0.88 ? "HIGH" : "MEDIUM",
        service_id: "operational",
        service_name: "Facility Operations Baseline",
        rule_violation: "None (Core safety staffing met)",
        ai_anomaly_score: aiScore,
        ai_status: aiStatus,
        critical_override_active: false,
        offline_generated: isOffline,
        message: `Edge AI detected an unusual staffing pattern (Score: ${aiScore.toFixed(2)}, Status: ${aiStatus}). ${aiExplanation}`,
        top_factors: factors.slice(0, 3),
        continuity_options: [],
        status: "ACTIVE"
      });
    }

    return fusedAlerts;
  }
}

// Global alert fusion engine singleton & window bindings
const alertFusionEngine = new AlertFusionEngine();
const alertFusion = alertFusionEngine;

if (typeof window !== "undefined") {
  window.AlertFusionEngine = AlertFusionEngine;
  window.alertFusionEngine = alertFusionEngine;
  window.alertFusion = alertFusion;
}
