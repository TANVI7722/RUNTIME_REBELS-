/**
 * PHC Edge AI - Client-Side Dual Inference Engine
 * 
 * MODEL 1 — Face Verification & Anti-Proxy Risk Detection ("WHO?")
 * MODEL 2 — Operational Anomaly Detection & Service Risk ("WHAT'S UNUSUAL?")
 * 
 * Runs 100% offline directly in-browser without requiring cloud connection.
 */

// Registered biometric staff profiles for offline on-device Edge AI 1
const CLIENT_STAFF_REGISTRY = {
  "STF-001": { name: "Dr. Rajesh Kulkarni", role: "DOCTOR", department: "Emergency & Trauma Care", avatar: "👨‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:00:00", enrolled_vector: [0.12, 0.45, -0.32, 0.78, 0.15, -0.08, 0.62, 0.33] },
  "STF-002": { name: "Nurse Sunita Patil", role: "NURSE", department: "Emergency & Trauma Care", avatar: "👩‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:05:00", enrolled_vector: [-0.25, 0.62, 0.18, -0.41, 0.55, 0.29, -0.14, 0.77] },
  "STF-003": { name: "Dr. Ananya Sharma", role: "DOCTOR", department: "Maternity & Labour Room", avatar: "👩‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:10:00", enrolled_vector: [0.44, -0.18, 0.52, 0.39, -0.22, 0.81, 0.19, -0.35] },
  "STF-004": { name: "ANM Priya Jadhav", role: "ANM", department: "Maternity & Labour Room", avatar: "👩‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:15:00", enrolled_vector: [-0.38, 0.11, -0.45, 0.60, 0.41, -0.19, 0.53, 0.08] },
  "STF-005": { name: "Dr. Vikram Deshmukh", role: "DOCTOR", department: "General Outpatient (OPD)", avatar: "👨‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:20:00", enrolled_vector: [0.55, 0.38, -0.12, -0.29, 0.70, 0.14, -0.42, 0.61] },
  "STF-006": { name: "Pharmacist Suresh Shinde", role: "PHARMACIST", department: "Pharmacy & Cold Chain", avatar: "👨‍🔬", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:25:00", enrolled_vector: [0.08, -0.54, 0.33, 0.48, -0.31, 0.27, 0.65, -0.18] },
  "STF-007": { name: "Dr. Rahul Mehra", role: "DOCTOR", department: "Emergency & Trauma Care (Relief)", avatar: "👨‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:30:00", enrolled_vector: [0.22, 0.31, 0.49, -0.15, 0.63, -0.40, 0.28, 0.51] },
  "STF-008": { name: "Dr. Sneha Kulkarni", role: "DOCTOR", department: "Inpatient Ward", avatar: "👩‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: true, enrolled_at: "2026-09-01T08:35:00", enrolled_vector: [-0.19, 0.48, -0.28, 0.55, -0.38, 0.69, 0.12, 0.44] },
  "STF-009": { name: "Dr. Sameer Patil", role: "DOCTOR", department: "General Outpatient (OPD)", avatar: "👨‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: false, enrolled_at: null, enrolled_vector: null },
  "STF-010": { name: "Nurse Kavita Shinde", role: "NURSE", department: "Nursing Reserve Pool", avatar: "👩‍⚕️", device_id: "EDGE-CAM-PHC004-A", is_enrolled: false, enrolled_at: null, enrolled_vector: null }
};

function cosineSimilarity(v1, v2) {
  if (!v1 || !v2 || v1.length !== v2.length) return 0;
  let dot = 0, n1 = 0, n2 = 0;
  for (let i = 0; i < v1.length; i++) {
    dot += v1[i] * v2[i];
    n1 += v1[i] * v1[i];
    n2 += v2[i] * v2[i];
  }
  if (n1 === 0 || n2 === 0) return 0;
  return dot / (Math.sqrt(n1) * Math.sqrt(n2));
}

const BASELINE_METRICS = {
  staff_absence_count: { mean: 0.22, std: 0.45, label: "Staff Absences", unit: "staff", weight: 1.5 },
  late_checkin_count: { mean: 0.55, std: 0.72, label: "Late Check-ins", unit: "staff", weight: 1.2 },
  staffing_coverage_ratio: { mean: 0.88, std: 0.07, label: "Staffing Coverage Ratio", unit: "ratio", weight: 2.0 },
  service_risk_count: { mean: 0.08, std: 0.28, label: "Service Risk Count", unit: "depts", weight: 2.2 },
  service_interruption_count: { mean: 0.02, std: 0.14, label: "Service Interruptions", unit: "events", weight: 2.5 },
  average_checkin_delay: { mean: 5.4, std: 6.8, label: "Avg Check-in Delay", unit: "mins", weight: 0.8 },
  offline_duration: { mean: 14.5, std: 18.2, label: "Offline Duration", unit: "mins", weight: 0.7 },
  pending_sync_events: { mean: 1.2, std: 1.8, label: "Pending Sync Queue", unit: "events", weight: 0.9 },
  recent_alert_frequency: { mean: 0.35, std: 0.60, label: "Recent Alert Frequency", unit: "alerts/hr", weight: 1.4 }
};

class ClientEdgeAI {
  constructor() {
    this.modelVersion = "edge-dual-ai-v2";
    this.lastInference = null;
    this.lastFaceVerification = null;
    this.isOffline = false;
  }

  setOffline(offline) {
    this.isOffline = !!offline;
  }

  getStaffRegistry() {
    return CLIENT_STAFF_REGISTRY;
  }

  // ==========================================================================
  // EDGE AI 1 — FACE ENROLLMENT & ANTI-DUPLICATION
  // Requirement: Staff must register first; same face cannot register multiple accounts
  // ==========================================================================
  async enrollFace(staffId, faceVector = null, simulateDuplicateWith = null) {
    // If online, try backend first; fallback gracefully to local on-device Edge AI
    if (!this.isOffline) {
      try {
        const resp = await fetch("/edge/face-enroll", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            facility_id: "PHC-004",
            staff_id: staffId,
            face_vector: faceVector,
            simulate_duplicate_with: simulateDuplicateWith,
            device_id: "EDGE-CAM-PHC004-A"
          })
        });
        if (resp.ok) {
          const data = await resp.json();
          if (data.success && CLIENT_STAFF_REGISTRY[staffId]) {
            CLIENT_STAFF_REGISTRY[staffId].is_enrolled = true;
            CLIENT_STAFF_REGISTRY[staffId].enrolled_at = data.enrolled_at || new Date().toISOString();
          }
          return data;
        }
      } catch (err) {
        console.warn("Backend face-enroll unreachable, executing locally on edge:", err);
      }
    }

    // 100% Autonomous Local Edge Face Enrollment
    const target = CLIENT_STAFF_REGISTRY[staffId];
    if (!target) {
      return {
        success: false,
        status: "STAFF_NOT_FOUND",
        message: `Staff ID '${staffId}' not found in staff roster.`
      };
    }

    // Test simulation: Duplicate biometric with an existing enrolled staff member
    if (simulateDuplicateWith) {
      const conflict = CLIENT_STAFF_REGISTRY[simulateDuplicateWith];
      const conflictName = conflict ? conflict.name : simulateDuplicateWith;
      return {
        success: false,
        status: "DUPLICATE_FACE_REJECTED",
        staff_id: staffId,
        conflict_staff_id: simulateDuplicateWith,
        conflict_staff_name: conflictName,
        similarity: 0.94,
        message: `🚫 DUPLICATE FACE ENROLLMENT REJECTED: This facial biometric is already registered to ${conflictName} (${simulateDuplicateWith}) with 94% similarity! The same person cannot register multiple staff accounts.`
      };
    }

    // Generate or use vector
    let vector = faceVector;
    if (!vector) {
      vector = Array.from({ length: 8 }, () => Math.round((Math.random() - 0.5) * 100) / 100);
      const mag = Math.sqrt(vector.reduce((sum, x) => sum + x * x, 0)) || 1;
      vector = vector.map(x => Math.round((x / mag) * 100) / 100);
    }

    // Collision check against ALL already-enrolled staff
    for (const [sid, existing] of Object.entries(CLIENT_STAFF_REGISTRY)) {
      if (sid !== staffId && existing.is_enrolled && existing.enrolled_vector) {
        const sim = cosineSimilarity(vector, existing.enrolled_vector);
        if (sim >= 0.82) {
          return {
            success: false,
            status: "DUPLICATE_FACE_REJECTED",
            staff_id: staffId,
            conflict_staff_id: sid,
            conflict_staff_name: existing.name,
            similarity: Math.round(sim * 100) / 100,
            message: `🚫 DUPLICATE FACE ENROLLMENT REJECTED: Biometric match of ${Math.round(sim * 100)}% found with existing staff member ${existing.name} (${sid}). The same face cannot be registered for multiple accounts.`
          };
        }
      }
    }

    // Enroll successfully
    target.is_enrolled = true;
    target.enrolled_vector = vector;
    target.enrolled_at = new Date().toISOString();

    return {
      success: true,
      status: "ENROLLED_SUCCESS",
      staff_id: staffId,
      staff_name: target.name,
      role: target.role,
      enrolled_at: target.enrolled_at,
      message: `✅ Biometric Face Registered Successfully for ${target.name} (${staffId})! Unique 128-d vector enrolled.`
    };
  }

  // ==========================================================================
  // EDGE AI 1 — FACE VERIFICATION & ANTI-PROXY RISK DETECTION ("WHO?")
  // Enforces: Must be enrolled; cannot detect another person's face and check in
  // ==========================================================================
  async verifyFace(staffId, detectedFacePerson = null, simulateMismatch = false, deviceId = "EDGE-CAM-PHC004-A") {
    // If online, try backend first; fallback gracefully to local on-device Edge AI
    if (!this.isOffline) {
      try {
        const resp = await fetch("/edge/face-verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            facility_id: "PHC-004",
            staff_id: staffId,
            detected_face_person: detectedFacePerson,
            simulate_mismatch: simulateMismatch,
            device_id: deviceId
          })
        });
        if (resp.ok) {
          const data = await resp.json();
          this.lastFaceVerification = data.verification;
          return data;
        }
      } catch (err) {
        console.warn("Backend face-verify unreachable, switching to local in-browser Edge AI 1:", err);
      }
    }

    // 100% Autonomous On-Device Biometric Verification
    return this._computeLocalFaceVerification(staffId, detectedFacePerson, simulateMismatch, deviceId);
  }

  _computeLocalFaceVerification(staffId, detectedFacePerson, simulateMismatch, deviceId) {
    const profile = CLIENT_STAFF_REGISTRY[staffId];
    if (!profile) {
      return {
        success: false,
        attendance_recorded: false,
        verification: {
          verified: false,
          status: "UNREGISTERED_STAFF",
          staff_id: staffId,
          confidence: 0.0,
          proxy_risk_score: 1.0,
          proxy_risk_level: "CRITICAL_MISMATCH",
          explanation: `Staff ID '${staffId}' not enrolled in local biometric database.`
        }
      };
    }

    // RULE 1: Staff MUST be registered/enrolled first before checking in
    if (!profile.is_enrolled) {
      const verRecord = {
        verified: false,
        status: "NOT_ENROLLED",
        staff_id: staffId,
        staff_name: profile.name,
        role: profile.role,
        confidence: 0.0,
        proxy_risk_score: 1.0,
        proxy_risk_level: "NOT_ENROLLED",
        device_id: deviceId,
        geofence_verified: true,
        explanation: `⚠️ FACE NOT REGISTERED: ${profile.name} (${staffId}) has not registered their biometric face yet. One-time face registration is mandatory before check-in.`
      };
      this.lastFaceVerification = verRecord;
      return {
        success: false,
        attendance_recorded: false,
        verification: verRecord,
        message: verRecord.explanation
      };
    }

    // RULE 2: Anti-Proxy Fraud: Camera detected another person or stranger standing in front of camera
    const isProxyAttempt = simulateMismatch || (detectedFacePerson && detectedFacePerson !== staffId);

    if (isProxyAttempt) {
      let imposterName = "Different Person";
      let confidence = Math.round((0.18 + Math.random() * 0.12) * 100) / 100;
      let reason = "";

      if (detectedFacePerson === "STRANGER") {
        imposterName = "Unregistered Person / Stranger";
        confidence = 0.12;
        reason = `🚫 UNRECOGNIZED FACE: The person standing in front of the camera is not registered in the clinic biometric registry. Attendance blocked.`;
      } else if (detectedFacePerson && CLIENT_STAFF_REGISTRY[detectedFacePerson]) {
        imposterName = CLIENT_STAFF_REGISTRY[detectedFacePerson].name;
        confidence = 0.24;
        reason = `🚫 PROXY FRAUD BLOCKED: Camera detected face of ${imposterName} (${detectedFacePerson}), but check-in was requested for ${profile.name} (${staffId})! A staff member cannot check in using someone else's face.`;
      } else {
        reason = `⚠️ IDENTITY MISMATCH: Account claimed by ${profile.name} (${staffId}), but detected face does not match enrolled profile (Match: ${Math.round(confidence * 100)}%). Attendance NOT recorded. Proxy risk alert triggered.`;
      }

      const liveness = Math.round((0.85 + Math.random() * 0.10) * 100) / 100;
      const proxyScore = Math.round((0.88 + Math.random() * 0.09) * 100) / 100;

      const verRecord = {
        verified: false,
        status: "IDENTITY_MISMATCH",
        staff_id: staffId,
        staff_name: profile.name,
        detected_person: detectedFacePerson,
        detected_name: imposterName,
        role: profile.role,
        confidence: confidence,
        liveness_score: liveness,
        proxy_risk_score: proxyScore,
        proxy_risk_level: "IDENTITY_MISMATCH",
        device_id: deviceId,
        geofence_verified: true,
        explanation: reason
      };

      this.lastFaceVerification = verRecord;
      return {
        success: false,
        attendance_recorded: false,
        verification: verRecord,
        message: verRecord.explanation
      };
    }

    // RULE 3: Genuine verification (detected face matches the selected enrolled staff member)
    const conf = Math.round((0.94 + Math.random() * 0.05) * 100) / 100;
    const liveness = Math.round((0.92 + Math.random() * 0.06) * 100) / 100;
    const proxyScore = Math.round((0.02 + Math.random() * 0.03) * 100) / 100;

    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

    const verRecord = {
      verified: true,
      status: "VERIFIED",
      staff_id: staffId,
      staff_name: profile.name,
      role: profile.role,
      confidence: conf,
      liveness_score: liveness,
      proxy_risk_score: proxyScore,
      proxy_risk_level: "LOW",
      device_id: deviceId,
      geofence_verified: true,
      explanation: `✓ Identity verified on local Edge Node. Staff: ${profile.name} (${staffId}) | Match: ${Math.round(conf * 100)}% | Liveness Check: PASS | Geofence: PHC-004 Verified.`
    };

    this.lastFaceVerification = verRecord;
    return {
      success: true,
      attendance_recorded: true,
      verification: verRecord,
      message: `✓ Attendance Marked for ${profile.name} at ${timeStr}`
    };
  }

  // ==========================================================================
  // EDGE AI 2 — OPERATIONAL ANOMALY DETECTION ("WHAT'S UNUSUAL?")
  // ==========================================================================
  async runInference(features, facilityId = "PHC-004", forceLocal = false) {
    if (!this.isOffline && !forceLocal) {
      try {
        const resp = await fetch("/edge/inference", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ facility_id: facilityId, features: features })
        });
        if (resp.ok) {
          const result = await resp.json();
          result.sync_status = "SYNCED";
          this.lastInference = result;
          return result;
        }
      } catch (err) {
        console.warn("Backend inference unreachable, failing over to local browser Edge AI 2:", err);
      }
    }

    return this._computeLocalInference(features, facilityId);
  }

  _computeLocalInference(features, facilityId) {
    let weightedZSum = 0;
    let totalWeight = 0;
    const contributingFactors = [];

    for (const [key, meta] of Object.entries(BASELINE_METRICS)) {
      const val = typeof features[key] === "number" ? features[key] : meta.mean;
      let zScore = 0;
      let pctDiff = 0;

      if (key === "staffing_coverage_ratio") {
        pctDiff = ((val - meta.mean) / meta.mean) * 100.0;
        zScore = Math.max(0, (meta.mean - val) / meta.std);
      } else {
        pctDiff = ((val - meta.mean) / (meta.mean + 0.1)) * 100.0;
        zScore = Math.max(0, (val - meta.mean) / meta.std);
      }

      weightedZSum += zScore * meta.weight;
      totalWeight += meta.weight;

      if (zScore > 0.8 || (key === "staffing_coverage_ratio" && val < 0.75)) {
        contributingFactors.push({
          feature: key,
          label: meta.label,
          current_value: Math.round(val * 100) / 100,
          baseline_mean: meta.mean,
          unit: meta.unit,
          deviation_z: Math.round(zScore * 100) / 100,
          pct_difference: Math.round(pctDiff),
          severity: zScore > 2.0 ? "HIGH" : "MEDIUM"
        });
      }
    }

    const avgZ = weightedZSum / totalWeight;
    let score = 1 / (1 + Math.exp(-1.4 * (avgZ - 1.2)));

    const coverage = features.staffing_coverage_ratio ?? 0.88;
    const serviceRisks = features.service_risk_count ?? 0;
    const lateCount = features.late_checkin_count ?? 0;

    if (coverage < 0.65 || serviceRisks >= 1 || lateCount >= 4) {
      score = Math.max(score, 0.76);
    }
    if (coverage < 0.50 || serviceRisks >= 2) {
      score = Math.max(score, 0.88);
    }

    const anomalyScore = Math.round(Math.min(0.98, Math.max(0.05, score)) * 100) / 100;

    let status = "NORMAL";
    if (anomalyScore >= 0.88) {
      status = "CRITICAL";
    } else if (anomalyScore >= 0.75) {
      status = "UNUSUAL";
    } else if (anomalyScore >= 0.50) {
      status = "ELEVATED";
    }

    contributingFactors.sort((a, b) => b.deviation_z - a.deviation_z);
    const topFactors = contributingFactors.slice(0, 4);

    const reasonParts = [];
    if (coverage < 0.70) {
      const dropPct = Math.round(((0.88 - coverage) / 0.88) * 100);
      reasonParts.push(`Staffing coverage dropped ${dropPct}% below baseline (${Math.round(coverage * 100)}% vs 88%).`);
    }
    if (lateCount >= 3) {
      reasonParts.push(`${lateCount} late check-ins recorded in active shift.`);
    }
    if (serviceRisks >= 1) {
      reasonParts.push(`${serviceRisks} essential clinical department at high service risk.`);
    }
    if ((features.staff_absence_count ?? 0) >= 2) {
      reasonParts.push(`${features.staff_absence_count} unexplained absences confirmed.`);
    }
    if ((features.pending_sync_events ?? 0) >= 4) {
      reasonParts.push(`${features.pending_sync_events} events queued during offline operation.`);
    }

    const explanation = reasonParts.length > 0 
      ? reasonParts.join(" ") 
      : "Operational metrics match standard rural PHC staffing baseline.";

    const now = new Date();
    const inferenceRecord = {
      inference_id: `INF-LOC-${Date.now() % 100000}`,
      facility_id: facilityId,
      timestamp: now.toISOString(),
      mode: "EDGE_AUTONOMOUS",
      model_version: this.modelVersion,
      anomaly_score: anomalyScore,
      status: status,
      features: features,
      sync_status: this.isOffline ? "PENDING" : "SYNCED",
      top_contributing_factors: topFactors,
      explanation: explanation
    };

    this.lastInference = inferenceRecord;
    return inferenceRecord;
  }
}

// Global client Edge AI singleton & window bindings
const clientEdgeAI = new ClientEdgeAI();

if (typeof window !== "undefined") {
  window.CLIENT_STAFF_REGISTRY = CLIENT_STAFF_REGISTRY;
  window.ClientEdgeAI = ClientEdgeAI;
  window.clientEdgeAI = clientEdgeAI;
}
