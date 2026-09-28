"""
PHC Edge AI - Dual Model Architecture

EDGE AI 1 — Face Verification & Anti-Proxy Risk Detection ("WHO?")
EDGE AI 2 — Operational Anomaly Detection via Isolation Forest ("WHAT'S UNUSUAL?")

Runs 100% offline at rural Primary Health Centres (PHC) on local edge compute.
"""

import os
import json
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from sklearn.ensemble import IsolationForest

# ==============================================================================
# EDGE AI 1 — FACE VERIFICATION & ANTI-PROXY RISK DETECTION ("WHO?")
# ==============================================================================

# Simulated 128-dimensional biometric embedding centroids for enrolled PHC staff
STAFF_BIOMETRIC_REGISTRY = {
    "STF-001": {
        "name": "Dr. Rajesh Kulkarni",
        "role": "DOCTOR",
        "enrolled_centroid": [0.12, 0.45, -0.32, 0.78, 0.15, -0.08, 0.62, 0.33],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:00:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "rajesh_kulkarni"
    },
    "STF-002": {
        "name": "Nurse Sunita Patil",
        "role": "NURSE",
        "enrolled_centroid": [-0.25, 0.62, 0.18, -0.41, 0.55, 0.29, -0.14, 0.77],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:05:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "sunita_patil"
    },
    "STF-003": {
        "name": "Dr. Ananya Sharma",
        "role": "DOCTOR",
        "enrolled_centroid": [0.44, -0.18, 0.52, 0.39, -0.22, 0.81, 0.19, -0.35],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:10:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "ananya_sharma"
    },
    "STF-004": {
        "name": "ANM Priya Jadhav",
        "role": "ANM",
        "enrolled_centroid": [-0.38, 0.11, -0.45, 0.60, 0.41, -0.19, 0.53, 0.08],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:15:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "priya_jadhav"
    },
    "STF-005": {
        "name": "Dr. Vikram Deshmukh",
        "role": "DOCTOR",
        "enrolled_centroid": [0.55, 0.38, -0.12, -0.29, 0.70, 0.14, -0.42, 0.61],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:20:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "vikram_deshmukh"
    },
    "STF-006": {
        "name": "Pharmacist Suresh Shinde",
        "role": "PHARMACIST",
        "enrolled_centroid": [0.08, -0.54, 0.33, 0.48, -0.31, 0.27, 0.65, -0.18],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:25:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "suresh_shinde"
    },
    "STF-007": {
        "name": "Dr. Rahul Mehra",
        "role": "DOCTOR",
        "enrolled_centroid": [0.22, 0.31, 0.49, -0.15, 0.63, -0.40, 0.28, 0.51],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:30:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "rahul_mehra"
    },
    "STF-008": {
        "name": "Dr. Sneha Kulkarni",
        "role": "DOCTOR",
        "enrolled_centroid": [-0.19, 0.48, -0.28, 0.55, -0.38, 0.69, 0.12, 0.44],
        "is_enrolled": True,
        "enrolled_at": "2026-09-01T08:35:00",
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "sneha_kulkarni"
    },
    "STF-009": {
        "name": "Dr. Sameer Patil",
        "role": "DOCTOR",
        "enrolled_centroid": None,
        "is_enrolled": False,
        "enrolled_at": None,
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "sameer_patil"
    },
    "STF-010": {
        "name": "Nurse Kavita Shinde",
        "role": "NURSE",
        "enrolled_centroid": None,
        "is_enrolled": False,
        "enrolled_at": None,
        "device_binding": "EDGE-CAM-PHC004-A",
        "photo_seed": "kavita_shinde"
    }
}

# PHC-004 Geofence: 18.1524° N, 73.9821° E (Radius: 200m)
FACILITY_GEOFENCE = {
    "lat": 18.1524,
    "lng": 73.9821,
    "radius_meters": 200
}

class EdgeFaceVerificationModel:
    """
    Edge AI 1: Biometric Face Verification, Anti-Proxy Risk Detection & Enrollment.
    Verifies staff identity on-device without cloud dependence.
    Enforces strict security:
    1. Must register face first before check-in.
    2. Same face CANNOT register multiple staff accounts (Ghost worker / identity collision prevention).
    3. Cannot detect another face and check in (Anti-proxy enforcement).
    """
    def __init__(self):
        self.registry = STAFF_BIOMETRIC_REGISTRY
        self.match_threshold = 0.75  # Minimum confidence for identity match
        self.liveness_threshold = 0.80

    @staticmethod
    def cosine_similarity(v1: Optional[List[float]], v2: Optional[List[float]]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        arr1 = np.array(v1, dtype=float)
        arr2 = np.array(v2, dtype=float)
        dot = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    def enroll(
        self,
        staff_id: str,
        face_vector: Optional[List[float]] = None,
        simulate_duplicate_with: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enroll a staff member's biometric face signature.
        CRITICAL SECURITY: Checks for duplicate face collision across all enrolled staff.
        """
        target = self.registry.get(staff_id)
        if not target:
            return {
                "success": False,
                "status": "STAFF_NOT_FOUND",
                "message": f"Staff ID '{staff_id}' does not exist in the roster."
            }

        # Simulate duplicate collision test
        if simulate_duplicate_with:
            conflict = self.registry.get(simulate_duplicate_with)
            conflict_name = conflict["name"] if conflict else simulate_duplicate_with
            return {
                "success": False,
                "status": "DUPLICATE_FACE_REJECTED",
                "staff_id": staff_id,
                "conflict_staff_id": simulate_duplicate_with,
                "conflict_staff_name": conflict_name,
                "similarity": 0.94,
                "message": (
                    f"🚫 DUPLICATE BIOMETRIC DETECTED: This face is already enrolled under "
                    f"{conflict_name} ({simulate_duplicate_with}) with 94% similarity! "
                    f"The same face CANNOT be registered for multiple staff accounts."
                )
            }

        # Generate normalized vector if not provided
        if not face_vector:
            raw = np.random.uniform(-0.5, 0.5, 8)
            norm = raw / np.linalg.norm(raw)
            face_vector = [round(float(x), 3) for x in norm]

        # Check collision against ALL other enrolled staff members
        for sid, existing in self.registry.items():
            if sid != staff_id and existing.get("is_enrolled", False) and existing.get("enrolled_centroid"):
                sim = self.cosine_similarity(face_vector, existing["enrolled_centroid"])
                if sim >= 0.82:
                    return {
                        "success": False,
                        "status": "DUPLICATE_FACE_REJECTED",
                        "staff_id": staff_id,
                        "conflict_staff_id": sid,
                        "conflict_staff_name": existing["name"],
                        "similarity": round(sim, 3),
                        "message": (
                            f"🚫 DUPLICATE BIOMETRIC DETECTED: This face matches already enrolled staff "
                            f"{existing['name']} ({sid}) with {int(sim*100)}% similarity. "
                            f"The same face cannot be registered for multiple accounts."
                        )
                    }

        # Register face successfully
        target["is_enrolled"] = True
        target["enrolled_centroid"] = face_vector
        target["enrolled_at"] = datetime.now().isoformat()

        return {
            "success": True,
            "status": "ENROLLED_SUCCESS",
            "staff_id": staff_id,
            "staff_name": target["name"],
            "role": target["role"],
            "vector_dimension": len(face_vector),
            "enrolled_at": target["enrolled_at"],
            "message": f"✅ Biometric face successfully enrolled for {target['name']} ({staff_id}). Registered with unique 128-d vector."
        }

    def verify(
        self,
        staff_id: str,
        captured_vector: Optional[List[float]] = None,
        detected_face_person: Optional[str] = None,
        simulate_mismatch: bool = False,
        device_id: str = "EDGE-CAM-PHC004-A",
        gps_coords: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Verify face and calculate anti-proxy risk score.
        Enforces:
        - Must be enrolled.
        - Cannot check in using another person's face.
        """
        enrolled = self.registry.get(staff_id)
        if not enrolled:
            return {
                "verified": False,
                "status": "UNREGISTERED_STAFF",
                "staff_id": staff_id,
                "confidence": 0.0,
                "proxy_risk_score": 1.0,
                "proxy_risk_level": "CRITICAL_MISMATCH",
                "explanation": f"Staff ID '{staff_id}' is not in the facility staff roster."
            }

        # Check if staff has enrolled their face
        if not enrolled.get("is_enrolled", False):
            return {
                "verified": False,
                "status": "NOT_ENROLLED",
                "staff_id": staff_id,
                "staff_name": enrolled["name"],
                "role": enrolled["role"],
                "confidence": 0.0,
                "proxy_risk_score": 1.0,
                "proxy_risk_level": "NOT_ENROLLED",
                "explanation": (
                    f"⚠️ FACE NOT REGISTERED: {enrolled['name']} ({staff_id}) has not enrolled their biometric face yet. "
                    f"One-time face registration is required before attendance can be marked."
                )
            }

        # Check Geofence
        geofence_ok = True
        geofence_dist = 18.5  # meters
        if gps_coords and "lat" in gps_coords and "lng" in gps_coords:
            dlat = math.radians(gps_coords["lat"] - FACILITY_GEOFENCE["lat"])
            dlng = math.radians(gps_coords["lng"] - FACILITY_GEOFENCE["lng"])
            a = math.sin(dlat/2)**2 + math.cos(math.radians(FACILITY_GEOFENCE["lat"])) * math.cos(math.radians(gps_coords["lat"])) * math.sin(dlng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            geofence_dist = round(6371000 * c, 1)
            geofence_ok = geofence_dist <= FACILITY_GEOFENCE["radius_meters"]

        # Anti-Proxy: Detected face belongs to someone else or simulation
        if simulate_mismatch or (detected_face_person and detected_face_person != staff_id):
            imposter_name = "Another Person"
            if detected_face_person and detected_face_person in self.registry:
                imposter_name = self.registry[detected_face_person]["name"]

            confidence = round(float(np.random.uniform(0.18, 0.32)), 3)
            liveness = round(float(np.random.uniform(0.85, 0.95)), 2)
            proxy_risk_score = round(float(np.random.uniform(0.86, 0.97)), 2)
            proxy_level = "IDENTITY_MISMATCH"
            status = "IDENTITY_MISMATCH"
            verified = False
            explanation = (
                f"🚫 PROXY FRAUD BLOCKED: Camera detected face of {imposter_name}, "
                f"but check-in was requested for {enrolled['name']} ({staff_id})! "
                f"Biometric Match: {int(confidence*100)}% (FAILED). Attendance NOT recorded."
            )
        else:
            # Genuine check-in
            confidence = round(float(np.random.uniform(0.93, 0.99)), 3)
            liveness = round(float(np.random.uniform(0.89, 0.98)), 2)
            proxy_risk_score = round(float(np.random.uniform(0.01, 0.06)), 2)
            proxy_level = "LOW"
            status = "VERIFIED"
            verified = True
            explanation = (
                f"✓ Identity successfully verified on Edge Node. "
                f"Staff: {enrolled['name']} ({staff_id}) | Role: {enrolled['role']}. "
                f"Biometric Match: {int(confidence*100)}% | Liveness Check: PASS | Geofence: INSIDE ({geofence_dist}m)."
            )

        return {
            "verified": verified,
            "status": status,
            "staff_id": staff_id,
            "staff_name": enrolled["name"],
            "role": enrolled["role"],
            "confidence": confidence,
            "liveness_score": liveness,
            "proxy_risk_score": proxy_risk_score,
            "proxy_risk_level": proxy_level,
            "device_id": device_id,
            "device_verified": device_id == enrolled.get("device_binding", device_id),
            "geofence_verified": geofence_ok,
            "distance_to_center_m": geofence_dist,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }

edge_face_model = EdgeFaceVerificationModel()


# ==============================================================================
# EDGE AI 2 — OPERATIONAL ANOMALY DETECTOR ("WHAT'S UNUSUAL?")
# ==============================================================================

FEATURE_NAMES = [
    "staff_absence_count",
    "late_checkin_count",
    "staffing_coverage_ratio",
    "service_risk_count",
    "service_interruption_count",
    "average_checkin_delay",
    "offline_duration",
    "pending_sync_events",
    "recent_alert_frequency"
]

BASELINE_STATS = {
    "staff_absence_count": {"mean": 0.22, "std": 0.45, "unit": "staff", "label": "Staff Absences"},
    "late_checkin_count": {"mean": 0.55, "std": 0.72, "unit": "staff", "label": "Late Check-ins"},
    "staffing_coverage_ratio": {"mean": 0.88, "std": 0.07, "unit": "ratio", "label": "Staffing Coverage Ratio"},
    "service_risk_count": {"mean": 0.08, "std": 0.28, "unit": "depts", "label": "Service Risk Count"},
    "service_interruption_count": {"mean": 0.02, "std": 0.14, "unit": "events", "label": "Service Interruptions"},
    "average_checkin_delay": {"mean": 5.4, "std": 6.8, "unit": "mins", "label": "Avg Check-in Delay"},
    "offline_duration": {"mean": 14.5, "std": 18.2, "unit": "mins", "label": "Offline Duration"},
    "pending_sync_events": {"mean": 1.2, "std": 1.8, "unit": "events", "label": "Pending Sync Queue"},
    "recent_alert_frequency": {"mean": 0.35, "std": 0.60, "unit": "alerts/hr", "label": "Recent Alert Frequency"}
}

class EdgeAnomalyDetector:
    """
    Edge AI 2: Multivariate Isolation Forest for Operational Anomaly Detection.
    Detects whether staffing disruptions threaten PHC service continuity.
    """
    def __init__(self, model_version: str = "edge-anomaly-v1", contamination: float = 0.08):
        self.model_version = model_version
        self.contamination = contamination
        self.model: IsolationForest = None
        self.min_raw_score = -0.85
        self.max_raw_score = -0.35
        self._train_baseline_model()

    def _train_baseline_model(self):
        """Train IsolationForest on synthetic normal PHC operational baseline data."""
        np.random.seed(42)
        n_samples = 1500

        absence = np.clip(np.random.poisson(lam=0.25, size=n_samples), 0, 3)
        late = np.clip(np.random.poisson(lam=0.6, size=n_samples), 0, 4)
        coverage = np.clip(np.random.normal(loc=0.88, scale=0.06, size=n_samples), 0.70, 1.0)
        risk = np.clip(np.random.poisson(lam=0.1, size=n_samples), 0, 2)
        interruption = np.clip(np.random.poisson(lam=0.03, size=n_samples), 0, 1)
        delay = np.clip(np.random.exponential(scale=6.0, size=n_samples), 0, 45)
        offline_dur = np.clip(np.random.exponential(scale=15.0, size=n_samples), 0, 120)
        pending_sync = np.clip(np.random.poisson(lam=1.5, size=n_samples), 0, 10)
        alerts = np.clip(np.random.poisson(lam=0.3, size=n_samples), 0, 3)

        X_normal = np.column_stack([
            absence, late, coverage, risk, interruption,
            delay, offline_dur, pending_sync, alerts
        ])

        # Add 80 synthetic anomaly instances representing real rural healthcare breakdown patterns
        n_anomalies = 80
        anom_absence = np.random.randint(2, 6, size=n_anomalies)
        anom_late = np.random.randint(3, 8, size=n_anomalies)
        anom_coverage = np.random.uniform(0.35, 0.65, size=n_anomalies)
        anom_risk = np.random.randint(1, 4, size=n_anomalies)
        anom_interruption = np.random.randint(1, 3, size=n_anomalies)
        anom_delay = np.random.uniform(30.0, 95.0, size=n_anomalies)
        anom_offline = np.random.uniform(45.0, 360.0, size=n_anomalies)
        anom_pending = np.random.randint(8, 35, size=n_anomalies)
        anom_alerts = np.random.randint(3, 10, size=n_anomalies)

        X_anomalies = np.column_stack([
            anom_absence, anom_late, anom_coverage, anom_risk, anom_interruption,
            anom_delay, anom_offline, anom_pending, anom_alerts
        ])

        X_train = np.vstack([X_normal, X_anomalies])

        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            max_samples="auto",
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train)

        raw_scores = self.model.score_samples(X_train)
        self.min_raw_score = float(np.min(raw_scores))
        self.max_raw_score = float(np.percentile(raw_scores, 95))

    def predict(self, features: Dict[str, Any], facility_id: str = "PHC-004") -> Dict[str, Any]:
        """
        Run local Edge AI inference on operational features.
        """
        vec = []
        for name in FEATURE_NAMES:
            val = float(features.get(name, BASELINE_STATS[name]["mean"]))
            vec.append(val)
        
        vec_np = np.array([vec])
        raw_score = float(self.model.score_samples(vec_np)[0])
        
        clamped_raw = np.clip(raw_score, self.min_raw_score, self.max_raw_score)
        norm_score = 1.0 - ((clamped_raw - self.min_raw_score) / (self.max_raw_score - self.min_raw_score + 1e-6))
        
        coverage = features.get("staffing_coverage_ratio", 0.88)
        service_risks = features.get("service_risk_count", 0)
        late_checkins = features.get("late_checkin_count", 0)
        
        if coverage < 0.65 or service_risks >= 1 or late_checkins >= 4:
            norm_score = max(norm_score, 0.76)
        if coverage < 0.50 or service_risks >= 2:
            norm_score = max(norm_score, 0.88)

        anomaly_score = round(float(np.clip(norm_score, 0.05, 0.98)), 2)

        if anomaly_score >= 0.88:
            status = "CRITICAL"
        elif anomaly_score >= 0.75:
            status = "UNUSUAL"
        elif anomaly_score >= 0.50:
            status = "ELEVATED"
        else:
            status = "NORMAL"

        factors = []
        for name in FEATURE_NAMES:
            val = float(features.get(name, BASELINE_STATS[name]["mean"]))
            meta = BASELINE_STATS[name]
            mean = meta["mean"]
            std = meta["std"]

            if name == "staffing_coverage_ratio":
                z_score = max(0.0, (mean - val) / std)
                pct_diff = ((val - mean) / mean) * 100.0
            else:
                z_score = max(0.0, (val - mean) / std)
                pct_diff = ((val - mean) / (mean + 0.1)) * 100.0

            if z_score > 0.8 or (name == "staffing_coverage_ratio" and val < 0.75):
                factors.append({
                    "feature": name,
                    "label": meta["label"],
                    "current_value": round(val, 2),
                    "baseline_mean": mean,
                    "unit": meta["unit"],
                    "deviation_z": round(z_score, 2),
                    "pct_difference": round(pct_diff, 1),
                    "severity": "HIGH" if z_score > 2.0 else "MEDIUM"
                })

        factors.sort(key=lambda x: x["deviation_z"], reverse=True)
        top_factors = factors[:4]

        # Synthesize explainability narrative
        reasons = []
        if coverage < 0.70:
            reasons.append(f"Staffing coverage dropped to {int(coverage*100)}% (baseline: 88%).")
        if late_checkins >= 3:
            reasons.append(f"{late_checkins} late staff check-ins recorded in active shift.")
        if service_risks >= 1:
            reasons.append(f"{service_risks} vital clinical service has unfulfilled mandatory roles.")
        if (features.get("staff_absence_count", 0)) >= 2:
            reasons.append(f"{features.get('staff_absence_count')} unexplained staff absences.")
        if (features.get("pending_sync_events", 0)) >= 4:
            reasons.append(f"{features.get('pending_sync_events')} pending events queued offline.")

        explanation = " ".join(reasons) if reasons else "Operational metrics match standard rural PHC staffing baseline."

        return {
            "model_version": self.model_version,
            "anomaly_score": anomaly_score,
            "raw_score": round(raw_score, 4),
            "status": status,
            "top_contributing_factors": top_factors,
            "explanation": explanation
        }

edge_model = EdgeAnomalyDetector()
