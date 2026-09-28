"""
FastAPI Endpoints for Edge Inference, Dual Edge AI Models,
Rule Fusion, Immutable Attendance Event Ledger, and Central Cloud Synchronization.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .model import (
    edge_model,
    edge_face_model,
    BASELINE_STATS,
    STAFF_BIOMETRIC_REGISTRY,
    FACILITY_GEOFENCE
)
from .face_engine import offline_face_engine
from .rules import rule_engine
from .database import (
    SessionLocal,
    FacilityRecord,
    StaffRecord,
    InferenceRecord,
    EventRecord,
    AlertRecord,
    SyncBatchRecord,
    AttendanceEventRecord,
    CorrectionRequestRecord,
    StaffContinuityPlanRecord,
    compute_event_hash
)
from .sync import sync_processor

app = FastAPI(
    title="PHC Edge AI - Local Intelligence & Cloud Sync Platform",
    description="Offline-First Operational AI Layer for Primary Health Centres (IPHS 2022 Grounded)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Schemas
class InferenceRequest(BaseModel):
    facility_id: str = "PHC-004"
    features: Dict[str, Any]

class FaceVerificationRequest(BaseModel):
    facility_id: str = "PHC-004"
    staff_id: str
    detected_face_person: Optional[str] = None
    simulate_mismatch: bool = False
    device_id: str = "EDGE-CAM-PHC004-A"
    gps_coords: Optional[Dict[str, float]] = None

class FaceEnrollmentRequest(BaseModel):
    facility_id: str = "PHC-004"
    staff_id: str
    face_vector: Optional[List[float]] = None
    simulate_duplicate_with: Optional[str] = None
    device_id: str = "EDGE-CAM-PHC004-A"

# --- 8-Step Offline Face Module Schemas ---
class StaffRegistrationRequest(BaseModel):
    facility_id: str = "PHC-004"
    staff_id: str
    name: str
    role: str  # DOCTOR, NURSE, ANM, PHARMACIST
    department: str
    scheduled_time: Optional[str] = "09:00"
    current_shift: Optional[str] = "09:00–17:00"
    consent: bool = True  # Step 1: Informed consent

class FaceImageCaptureRequest(BaseModel):
    facility_id: str = "PHC-004"
    staff_id: str
    image_base64: str  # Step 2: Captured image
    consent: bool = True

class FaceRecognizeCameraRequest(BaseModel):
    facility_id: str = "PHC-004"
    image_base64: str  # Camera image for 1:N recognition
    device_id: str = "EDGE-CAM-PHC004-A"
    record_attendance: bool = True  # Step 7: Record attendance if match found

class AttendanceCheckinRequest(BaseModel):
    facility_id: str = "PHC-004"
    staff_id: str
    verification_method: str = "FACE_EDGE"  # FACE_EDGE, MANUAL_AUTHORIZED
    device_id: str = "EDGE-CAM-PHC004-A"
    proxy_risk_score: float = 0.0
    notes: Optional[str] = None

class CorrectionSubmitRequest(BaseModel):
    facility_id: str = "PHC-004"
    original_event_id: str
    staff_id: str
    reason: str
    proposed_status: str
    requested_by: str = "Duty Nurse / Staff"

class CorrectionReviewRequest(BaseModel):
    correction_id: str
    action: str  # APPROVE, REJECT
    reviewed_by: str = "PHC Medical Officer In-Charge"
    admin_notes: Optional[str] = None

class ContinuityAuthorizeRequest(BaseModel):
    facility_id: str = "PHC-004"
    service_id: str
    service_name: str
    unavailable_staff_id: str
    unavailable_staff_name: str
    option_type: str  # RELIEF_ASSIGNMENT, OVERTIME_REQUEST, ESCALATION_REFERRAL
    assigned_staff_id: Optional[str] = None
    assigned_staff_name: Optional[str] = None
    details: str
    authorized_by: str = "Medical Superintendent"

class ShiftEvaluationRequest(BaseModel):
    facility_id: str = "PHC-004"
    offline_mode: bool = False
    staff_roster: Optional[List[Dict[str, Any]]] = None
    override_features: Optional[Dict[str, Any]] = None

class SyncBatchRequest(BaseModel):
    facility_id: str = "PHC-004"
    batch_id: Optional[str] = None
    inferences: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    attendance_events: List[Dict[str, Any]] = []
    corrections: List[Dict[str, Any]] = []
    continuity_plans: List[Dict[str, Any]] = []

class StaffUpdateRequest(BaseModel):
    staff_id: str
    facility_id: str = "PHC-004"
    status: str
    checkin_time: Optional[str] = None
    delay_minutes: Optional[int] = 0

# --- Health & Reference Endpoints ---

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "PHC Edge AI Platform",
        "models": {
            "edge_ai_1": "Biometric Face & Anti-Proxy Risk Verification",
            "edge_ai_2": edge_model.model_version
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/baseline-stats")
def get_baseline_stats():
    """Return operational baseline stats for explainability charts."""
    return BASELINE_STATS

@app.get("/api/reference/iphs")
def get_iphs_reference():
    """
    Section 12: Real-World Research Reference Mode.
    Returns real-world IPHS 2022 guidelines context, 15% leave/training reserve principle,
    and Maharashtra attendance references.
    """
    return {
        "title": "Indian Public Health Standards (IPHS 2022) & Operational Reference",
        "guidelines": {
            "source": "National Health Mission, Ministry of Health and Family Welfare (MoHFW), Govt of India",
            "document": "IPHS 2022 Revised Guidelines for Sub-District & Primary Health Centres",
            "leave_reserve_norm": (
                "IPHS 2022 explicitly discusses arrangements to cover leave and holidays and notes "
                "that states can determine leave reserves; it recommends a 15% leave/training reserve "
                "or the applicable state rule for staff."
            ),
            "state_biometric_system": "Government of Maharashtra Aadhaar-Enabled Biometric Attendance System (attendance.maharashtra.gov.in)",
            "proxy_prevention": "Central Water Commission & state instructions on biometric, facial recognition, and geofencing safeguards."
        },
        "configurable_staffing_rules": {
            "is_demo_configuration": True,
            "emergency_min_doctors": 1,
            "emergency_min_nurses": 1,
            "maternity_min_doctors": 1,
            "maternity_min_anm": 1,
            "opd_min_doctors": 1,
            "pharmacy_min_pharmacists": 1,
            "leave_reserve_target_pct": 15,
            "late_threshold_minutes": 15,
            "overtime_max_hours": 2.0,
            "facility_geofence": FACILITY_GEOFENCE
        }
    }

# --- 8-STEP OFFLINE FACE RECOGNITION MODULE ENDPOINTS ---

@app.post("/api/face/staff/register")
def register_phc_staff(req: StaffRegistrationRequest):
    """
    Step 1: Collect staff details – Register PHC staff with their ID and basic details.
    """
    db = SessionLocal()
    try:
        existing = db.query(StaffRecord).filter(StaffRecord.staff_id == req.staff_id).first()
        if existing:
            existing.name = req.name
            existing.role = req.role
            existing.department = req.department
            existing.scheduled_time = req.scheduled_time
            existing.current_shift = req.current_shift
            existing.face_consent = req.consent
            msg = f"Updated existing staff record for {req.name} ({req.staff_id})"
        else:
            new_staff = StaffRecord(
                staff_id=req.staff_id,
                facility_id=req.facility_id,
                name=req.name,
                role=req.role,
                department=req.department,
                scheduled_time=req.scheduled_time,
                current_shift=req.current_shift,
                status="SCHEDULED",
                face_consent=req.consent,
                is_reserve=False
            )
            db.add(new_staff)
            msg = f"Registered new PHC staff member {req.name} ({req.staff_id})"

        db.commit()
        return {
            "success": True,
            "staff_id": req.staff_id,
            "name": req.name,
            "role": req.role,
            "department": req.department,
            "consent_recorded": req.consent,
            "message": msg
        }
    finally:
        db.close()


@app.post("/api/face/capture-and-enroll")
def capture_and_enroll_face(req: FaceImageCaptureRequest):
    """
    Steps 2, 3, 4, 5:
    2. Capture face image (base64)
    3. Detect face with OpenCV (Haar/DNN)
    4. Generate face embedding with ArcFace/FaceNet-compatible deep embedder (512-D)
    5. Store staff ID and face embedding in the database
    """
    if not req.consent:
        raise HTTPException(status_code=400, detail="Informed consent is mandatory for facial biometric enrollment.")

    img = offline_face_engine.decode_image(req.image_base64)
    if img is None:
        raise HTTPException(status_code=400, detail="Failed to decode image data.")

    # Step 3: Detect face using OpenCV
    detection = offline_face_engine.detect_face(img)
    if detection is None or detection["face_roi"].size == 0:
        raise HTTPException(status_code=400, detail="No face detected in the captured image. Ensure clear lighting.")

    # Step 4: Extract 512-D ArcFace embedding
    embedding = offline_face_engine.extract_embedding(detection["face_roi"])

    # Step 5: Store in SQLite database
    db = SessionLocal()
    try:
        staff_rec = db.query(StaffRecord).filter(StaffRecord.staff_id == req.staff_id).first()
        if not staff_rec:
            # Create staff profile if not already present
            staff_rec = StaffRecord(
                staff_id=req.staff_id,
                facility_id=req.facility_id,
                name=f"Staff {req.staff_id}",
                role="STAFF",
                department="General Clinical Services",
                status="SCHEDULED"
            )
            db.add(staff_rec)

        now_iso = datetime.now().isoformat()
        staff_rec.face_embedding = json.dumps(embedding)
        staff_rec.face_consent = True
        staff_rec.face_enrolled_at = now_iso

        # Also update in-memory registry for Edge AI model synchronization
        if req.staff_id in edge_face_model.registry:
            edge_face_model.registry[req.staff_id]["is_enrolled"] = True
            edge_face_model.registry[req.staff_id]["enrolled_centroid"] = embedding[:8]
            edge_face_model.registry[req.staff_id]["enrolled_at"] = now_iso

        db.commit()

        return {
            "success": True,
            "step": "5_STORE_DATA",
            "staff_id": req.staff_id,
            "staff_name": staff_rec.name,
            "face_detected": detection["detected"],
            "bbox": detection["bbox"],
            "embedding_dimension": len(embedding),
            "enrolled_at": now_iso,
            "message": f"Step 1-5 Complete: Face detected by OpenCV, 512-D ArcFace embedding generated and stored in database for {staff_rec.name}."
        }
    finally:
        db.close()


@app.post("/api/face/recognize-and-attend")
def recognize_and_record_attendance(req: FaceRecognizeCameraRequest):
    """
    Steps 6, 7, 8:
    6. Recognize face – Compare camera face embedding with stored embeddings.
    7. Record attendance – If match found, identify staff member and record immutable attendance.
    8. Return clean JSON for the web application.
    """
    img = offline_face_engine.decode_image(req.image_base64)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image payload.")

    # Detect face using OpenCV
    detection = offline_face_engine.detect_face(img)
    if detection is None or detection["face_roi"].size == 0:
        return {
            "success": False,
            "face_detected": False,
            "attendance_recorded": False,
            "message": "No face found in camera frame."
        }

    # Generate camera face embedding
    query_embedding = offline_face_engine.extract_embedding(detection["face_roi"])

    # Load enrolled staff embeddings from database
    db = SessionLocal()
    try:
        staff_list = db.query(StaffRecord).filter(
            StaffRecord.facility_id == req.facility_id,
            StaffRecord.face_embedding.isnot(None)
        ).all()

        enrolled_db = []
        for s in staff_list:
            try:
                emb = json.loads(s.face_embedding)
                enrolled_db.append({
                    "staff_id": s.staff_id,
                    "staff_name": s.name,
                    "role": s.role,
                    "department": s.department,
                    "face_embedding": emb
                })
            except Exception:
                continue

        # Step 6: Recognize face by cosine similarity
        match_result = offline_face_engine.recognize_face(query_embedding, enrolled_db)

        if not match_result["matched"] or not match_result["staff_id"]:
            return {
                "success": False,
                "face_detected": True,
                "bbox": detection["bbox"],
                "match_result": match_result,
                "attendance_recorded": False,
                "message": match_result["message"]
            }

        matched_staff_id = match_result["staff_id"]
        matched_name = match_result["staff_name"]

        # Step 7: Record attendance in append-only immutable ledger
        attendance_info = None
        if req.record_attendance:
            last_ev = db.query(AttendanceEventRecord).filter(
                AttendanceEventRecord.facility_id == req.facility_id
            ).order_by(AttendanceEventRecord.timestamp.desc()).first()

            prev_id = last_ev.event_id if last_ev else "GENESIS-PHC004"
            event_id = f"ATT-EV-{int(datetime.now().timestamp()*1000) % 1000000}"
            now_iso = datetime.now().isoformat()
            now_time = datetime.now().strftime("%H:%M")

            event_hash = compute_event_hash(event_id, matched_staff_id, now_iso, "ATTENDANCE_CHECKIN", prev_id)

            att_event = AttendanceEventRecord(
                event_id=event_id,
                facility_id=req.facility_id,
                staff_id=matched_staff_id,
                staff_name=matched_name,
                timestamp=now_iso,
                event_type="ATTENDANCE_CHECKIN",
                status_code="PRESENT",
                device_id=req.device_id,
                verification_method="FACE_OPENCV_ARCFACE",
                proxy_risk_score=round(max(0.0, 1.0 - match_result["similarity"]), 3),
                proxy_risk_level="LOW",
                created_by="OFFLINE_FACE_ENGINE",
                sync_status="SYNCED",
                previous_event_id=prev_id,
                event_hash=event_hash,
                notes=f"Offline OpenCV+ArcFace Recognition (Match: {int(match_result['similarity']*100)}%)"
            )
            db.add(att_event)

            # Update staff roster status
            target_staff = db.query(StaffRecord).filter(StaffRecord.staff_id == matched_staff_id).first()
            if target_staff:
                target_staff.status = "PRESENT"
                target_staff.checkin_time = now_time

            db.commit()

            attendance_info = {
                "event_id": event_id,
                "status": "PRESENT",
                "checkin_time": now_time,
                "event_hash": event_hash,
                "method": "FACE_OPENCV_ARCFACE"
            }

        return {
            "success": True,
            "face_detected": True,
            "bbox": detection["bbox"],
            "match_result": match_result,
            "attendance_recorded": req.record_attendance,
            "attendance_info": attendance_info,
            "message": f"Step 6 & 7 Complete: Face recognized as {matched_name} ({matched_staff_id}) with {int(match_result['similarity']*100)}% similarity. Attendance recorded."
        }
    finally:
        db.close()


@app.get("/api/face/enrolled-staff")
def get_enrolled_staff_list(facility_id: str = "PHC-004"):
    """
    Returns list of staff members with their biometric enrollment and consent status.
    """
    db = SessionLocal()
    try:
        records = db.query(StaffRecord).filter(StaffRecord.facility_id == facility_id).all()
        return [
            {
                "staff_id": s.staff_id,
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "is_enrolled": s.face_embedding is not None,
                "consent": bool(s.face_consent),
                "enrolled_at": s.face_enrolled_at or ("Pre-enrolled Baseline" if s.face_embedding else None),
                "status": s.status,
                "checkin_time": s.checkin_time
            }
            for s in records
        ]
    finally:
        db.close()


# --- EDGE AI 1: Biometric Face Verification, Anti-Proxy & Enrollment Endpoints ---

@app.post("/edge/face-enroll")
def edge_face_enroll(req: FaceEnrollmentRequest):
    """
    Edge AI 1: One-time staff face registration & anti-duplication enforcement.
    Ensures:
    1. Must register face first before check-in.
    2. Same face CANNOT be registered for multiple accounts.
    """
    res = edge_face_model.enroll(
        staff_id=req.staff_id,
        face_vector=req.face_vector,
        simulate_duplicate_with=req.simulate_duplicate_with
    )
    return res

@app.get("/edge/face-registry")
def edge_face_registry():
    """
    Returns biometric enrollment status for all staff in PHC-004.
    """
    return [
        {
            "staff_id": sid,
            "name": data["name"],
            "role": data["role"],
            "is_enrolled": data.get("is_enrolled", False),
            "enrolled_at": data.get("enrolled_at", "Pre-enrolled Baseline" if data.get("is_enrolled") else None)
        }
        for sid, data in edge_face_model.registry.items()
    ]

@app.post("/edge/face-verify")
def edge_face_verification(req: FaceVerificationRequest):
    """
    Edge AI 1: Biometric Face Verification & Anti-Proxy Risk Detection.
    Verifies staff face on edge device. If verified and not mismatch,
    appends an immutable AttendanceEventRecord.
    """
    db = SessionLocal()
    try:
        # Run Edge AI 1 model with detected face and anti-proxy check
        result = edge_face_model.verify(
            staff_id=req.staff_id,
            detected_face_person=req.detected_face_person,
            simulate_mismatch=req.simulate_mismatch,
            device_id=req.device_id,
            gps_coords=req.gps_coords
        )

        # If identity mismatch detected, record security alert event; do NOT mark attendance
        if not result["verified"]:
            mismatch_event = EventRecord(
                event_id=f"EV-PROXY-{int(datetime.now().timestamp()*1000)}",
                facility_id=req.facility_id,
                timestamp=datetime.now().isoformat(),
                event_type="PROXY_ATTENDANCE_MISMATCH",
                payload=json.dumps({
                    "staff_id": req.staff_id,
                    "confidence": result["confidence"],
                    "proxy_risk_score": result["proxy_risk_score"],
                    "reason": result["explanation"],
                    "device_id": req.device_id
                }),
                priority="HIGH",
                sync_status="SYNCED"
            )
            db.add(mismatch_event)
            db.commit()
            return {
                "success": False,
                "verification": result,
                "attendance_recorded": False,
                "message": result["explanation"]
            }

        # Identity verified! Append immutable Attendance Event to the ledger
        last_ev = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == req.facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).first()

        prev_id = last_ev.event_id if last_ev else "GENESIS-PHC004"
        event_id = f"ATT-EV-{int(datetime.now().timestamp()*1000) % 1000000}"
        now_iso = datetime.now().isoformat()
        event_hash = compute_event_hash(event_id, req.staff_id, now_iso, "ATTENDANCE_CHECKIN", prev_id)

        att_event = AttendanceEventRecord(
            event_id=event_id,
            facility_id=req.facility_id,
            staff_id=req.staff_id,
            staff_name=result["staff_name"],
            timestamp=now_iso,
            event_type="ATTENDANCE_CHECKIN",
            status_code="PRESENT",
            device_id=req.device_id,
            verification_method="FACE_EDGE",
            proxy_risk_score=result["proxy_risk_score"],
            proxy_risk_level=result["proxy_risk_level"],
            created_by="EDGE_FACE_AI",
            sync_status="SYNCED",
            previous_event_id=prev_id,
            event_hash=event_hash,
            notes=f"Edge AI Face Verified (Confidence: {int(result['confidence']*100)}%)"
        )
        db.add(att_event)

        # Update staff record in roster
        staff_rec = db.query(StaffRecord).filter(StaffRecord.staff_id == req.staff_id).first()
        if staff_rec:
            staff_rec.status = "PRESENT"
            staff_rec.checkin_time = datetime.now().strftime("%H:%M")
            staff_rec.delay_minutes = 0

        db.commit()

        return {
            "success": True,
            "verification": result,
            "attendance_recorded": True,
            "attendance_event": {
                "event_id": att_event.event_id,
                "timestamp": att_event.timestamp,
                "status_code": att_event.status_code,
                "event_hash": att_event.event_hash,
                "previous_event_id": att_event.previous_event_id
            },
            "message": f"✓ Attendance Marked for {result['staff_name']} at {datetime.now().strftime('%H:%M:%S')}"
        }
    finally:
        db.close()

# --- Append-Only Event Ledger & Correction Workflow Endpoints ---

@app.get("/api/attendance/events/{facility_id}")
def get_attendance_events(facility_id: str):
    """
    Returns the immutable append-only attendance event ledger.
    Attendance once marked cannot be edited or deleted.
    """
    db = SessionLocal()
    try:
        events = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).all()

        return [
            {
                "event_id": e.event_id,
                "facility_id": e.facility_id,
                "staff_id": e.staff_id,
                "staff_name": e.staff_name,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "status_code": e.status_code,
                "device_id": e.device_id,
                "verification_method": e.verification_method,
                "proxy_risk_score": e.proxy_risk_score,
                "proxy_risk_level": e.proxy_risk_level,
                "created_by": e.created_by,
                "sync_status": e.sync_status,
                "previous_event_id": e.previous_event_id,
                "event_hash": e.event_hash,
                "notes": e.notes
            }
            for e in events
        ]
    finally:
        db.close()

@app.post("/api/attendance/correction-request")
def request_attendance_correction(req: CorrectionSubmitRequest):
    """
    Correction Workflow:
    Original attendance event remains permanent in audit trail.
    Appends a new CORRECTION_REQUESTED event for supervisor review.
    """
    db = SessionLocal()
    try:
        orig = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.event_id == req.original_event_id
        ).first()
        if not orig:
            raise HTTPException(status_code=404, detail="Original attendance event not found")

        cid = f"CORR-{int(datetime.now().timestamp()*1000) % 100000}"
        now_iso = datetime.now().isoformat()

        corr = CorrectionRequestRecord(
            correction_id=cid,
            original_event_id=req.original_event_id,
            facility_id=req.facility_id,
            staff_id=req.staff_id,
            staff_name=orig.staff_name,
            requested_by=req.requested_by,
            requested_at=now_iso,
            reason=req.reason,
            proposed_status=req.proposed_status,
            status="PENDING"
        )
        db.add(corr)

        # Append to immutable attendance ledger as CORRECTION_REQUESTED
        last_ev = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == req.facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).first()

        prev_id = last_ev.event_id if last_ev else "GENESIS"
        eid = f"ATT-EV-{int(datetime.now().timestamp()*1000) % 1000000}"
        ehash = compute_event_hash(eid, req.staff_id, now_iso, "CORRECTION_REQUESTED", prev_id)

        att_ev = AttendanceEventRecord(
            event_id=eid,
            facility_id=req.facility_id,
            staff_id=req.staff_id,
            staff_name=orig.staff_name,
            timestamp=now_iso,
            event_type="CORRECTION_REQUESTED",
            status_code=req.proposed_status,
            device_id="PORTAL-ADMIN",
            verification_method="MANUAL_AUTHORIZED",
            proxy_risk_score=0.0,
            proxy_risk_level="LOW",
            created_by=req.requested_by,
            sync_status="SYNCED",
            previous_event_id=prev_id,
            event_hash=ehash,
            notes=f"Correction requested for {orig.event_id}. Reason: {req.reason}"
        )
        db.add(att_ev)
        db.commit()

        return {
            "status": "SUCCESS",
            "correction_id": cid,
            "message": "Correction request submitted. Original event remains permanently in audit trail."
        }
    finally:
        db.close()

@app.post("/api/attendance/correction-review")
def review_attendance_correction(req: CorrectionReviewRequest):
    """
    Admin reviews correction request. If approved, appends CORRECTION_APPROVED event
    and updates effective roster status while keeping full audit history.
    """
    db = SessionLocal()
    try:
        corr = db.query(CorrectionRequestRecord).filter(
            CorrectionRequestRecord.correction_id == req.correction_id
        ).first()
        if not corr:
            raise HTTPException(status_code=404, detail="Correction request not found")

        corr.status = "APPROVED" if req.action.upper() == "APPROVE" else "REJECTED"
        corr.reviewed_by = req.reviewed_by
        corr.reviewed_at = datetime.now().isoformat()
        corr.admin_notes = req.admin_notes

        now_iso = datetime.now().isoformat()
        last_ev = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == corr.facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).first()

        prev_id = last_ev.event_id if last_ev else "GENESIS"
        eid = f"ATT-EV-{int(datetime.now().timestamp()*1000) % 1000000}"
        event_type = "CORRECTION_APPROVED" if req.action.upper() == "APPROVE" else "CORRECTION_REJECTED"
        ehash = compute_event_hash(eid, corr.staff_id, now_iso, event_type, prev_id)

        att_ev = AttendanceEventRecord(
            event_id=eid,
            facility_id=corr.facility_id,
            staff_id=corr.staff_id,
            staff_name=corr.staff_name,
            timestamp=now_iso,
            event_type=event_type,
            status_code=corr.proposed_status if req.action.upper() == "APPROVE" else "ORIGINAL_RETAINED",
            device_id="ADMIN-CONSOLE",
            verification_method="MANUAL_AUTHORIZED",
            proxy_risk_score=0.0,
            proxy_risk_level="LOW",
            created_by=req.reviewed_by,
            sync_status="SYNCED",
            previous_event_id=prev_id,
            event_hash=ehash,
            notes=f"Admin {req.reviewed_by} marked {event_type}. Notes: {req.admin_notes or 'Approved after review'}"
        )
        db.add(att_ev)

        # If approved, update active roster status
        if req.action.upper() == "APPROVE":
            s_rec = db.query(StaffRecord).filter(StaffRecord.staff_id == corr.staff_id).first()
            if s_rec:
                s_rec.status = corr.proposed_status

        db.commit()
        return {
            "status": "SUCCESS",
            "correction_status": corr.status,
            "message": f"Correction {corr.status.lower()} by {req.reviewed_by}."
        }
    finally:
        db.close()

# --- Staff Continuity Engine Authorization Endpoints ---

@app.post("/api/continuity/authorize")
def authorize_continuity_plan(req: ContinuityAuthorizeRequest):
    """
    Staff Continuity / Overtime Authorization:
    System recommends options (Option A: Relief, Option B: Overtime, Option C: Escalate),
    and Administrator must explicitly authorize.
    Appends REPLACEMENT_ASSIGNED or OVERTIME_APPROVED event.
    """
    db = SessionLocal()
    try:
        now_iso = datetime.now().isoformat()
        plan_id = f"CONT-PLAN-{int(datetime.now().timestamp()*1000) % 100000}"

        plan = StaffContinuityPlanRecord(
            plan_id=plan_id,
            facility_id=req.facility_id,
            service_id=req.service_id,
            service_name=req.service_name,
            unavailable_staff_id=req.unavailable_staff_id,
            unavailable_staff_name=req.unavailable_staff_name,
            option_type=req.option_type,
            assigned_staff_id=req.assigned_staff_id,
            assigned_staff_name=req.assigned_staff_name,
            details=req.details,
            status="AUTHORIZED",
            authorized_by=req.authorized_by,
            authorized_at=now_iso,
            timestamp=now_iso
        )
        db.add(plan)

        # Update unavailable staff status to COVERED_ABSENCE / REPLACED
        unavail = db.query(StaffRecord).filter(StaffRecord.staff_id == req.unavailable_staff_id).first()
        if unavail:
            unavail.status = "COVERED_ABSENCE"

        # If replacement assigned, update assigned staff status to PRESENT on that shift
        if req.assigned_staff_id:
            assigned = db.query(StaffRecord).filter(StaffRecord.staff_id == req.assigned_staff_id).first()
            if assigned:
                if req.option_type == "RELIEF_ASSIGNMENT":
                    assigned.status = "PRESENT"
                    assigned.checkin_time = datetime.now().strftime("%H:%M")
                elif req.option_type == "OVERTIME_REQUEST":
                    assigned.workload_hours = float(assigned.workload_hours or 8.0) + 2.0

        # Append immutable audit event
        last_ev = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == req.facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).first()

        prev_id = last_ev.event_id if last_ev else "GENESIS"
        eid = f"ATT-EV-{int(datetime.now().timestamp()*1000) % 1000000}"
        event_type = "REPLACEMENT_ASSIGNED" if req.option_type == "RELIEF_ASSIGNMENT" else "OVERTIME_APPROVED"
        ehash = compute_event_hash(eid, req.assigned_staff_id or "NONE", now_iso, event_type, prev_id)

        att_ev = AttendanceEventRecord(
            event_id=eid,
            facility_id=req.facility_id,
            staff_id=req.assigned_staff_id or req.unavailable_staff_id,
            staff_name=req.assigned_staff_name or req.unavailable_staff_name,
            timestamp=now_iso,
            event_type=event_type,
            status_code="COVERED_ABSENCE",
            device_id="ADMIN-CONSOLE",
            verification_method="MANUAL_AUTHORIZED",
            proxy_risk_score=0.0,
            proxy_risk_level="LOW",
            created_by=req.authorized_by,
            sync_status="SYNCED",
            previous_event_id=prev_id,
            event_hash=ehash,
            notes=f"Continuity Action: {req.option_type} authorized for {req.service_name}. {req.details}"
        )
        db.add(att_ev)
        db.commit()

        return {
            "status": "SUCCESS",
            "plan_id": plan_id,
            "message": f"Staff continuity action authorized by {req.authorized_by}. Service coverage restored."
        }
    finally:
        db.close()

# --- EDGE AI 2: Operational Anomaly & Shift Evaluation ---

@app.post("/edge/inference")
def local_edge_inference(req: InferenceRequest):
    """
    Edge AI 2: Lightweight local inference running Isolation Forest.
    """
    inf_res = edge_model.predict(req.features, facility_id=req.facility_id)
    inference_id = f"INF-{int(datetime.now().timestamp()*1000) % 100000}"

    record = {
        "inference_id": inference_id,
        "facility_id": req.facility_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "EDGE",
        "model_version": inf_res["model_version"],
        "anomaly_score": inf_res["anomaly_score"],
        "status": inf_res["status"],
        "features": req.features,
        "sync_status": "PENDING",
        "raw_score": inf_res["raw_score"],
        "top_contributing_factors": inf_res["top_contributing_factors"],
        "explanation": inf_res["explanation"]
    }
    return record

@app.post("/edge/evaluate-shift")
def evaluate_shift(req: ShiftEvaluationRequest):
    """
    Combined Edge Reasoning Workflow:
    1. Evaluates deterministic healthcare rules against current staff roster
    2. Runs Leave & Absenteeism Intelligence
    3. Builds dynamic feature vector
    4. Runs Edge AI Isolation Forest inference
    5. Performs Alert Fusion with Critical Alert Override & Continuity Options
    """
    db = SessionLocal()
    try:
        # Load all staff from DB including reserve staff
        staff_rows = db.query(StaffRecord).filter(StaffRecord.facility_id == req.facility_id).all()
        full_pool = [
            {
                "staff_id": s.staff_id,
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "status": s.status,
                "scheduled_time": s.scheduled_time,
                "current_shift": s.current_shift,
                "checkin_time": s.checkin_time,
                "delay_minutes": s.delay_minutes,
                "leave_status": s.leave_status,
                "leave_approved": s.leave_approved,
                "leave_reason": s.leave_reason,
                "is_reserve": s.is_reserve,
                "qualified_services": s.qualified_services,
                "workload_hours": s.workload_hours
            }
            for s in staff_rows
        ]

        # If custom roster passed in request, use it for active shift
        roster = req.staff_roster if req.staff_roster else full_pool

        # 1. Deterministic Rule Engine
        rule_eval = rule_engine.evaluate_services(roster)

        # 2. Extract operational features
        absence_count = sum(1 for s in roster if rule_engine.classify_attendance_state(s) in ["ABSENT", "UNAUTHORIZED_ABSENCE"])
        late_count = sum(1 for s in roster if rule_engine.classify_attendance_state(s) == "LATE" or (s.get("delay_minutes", 0) > 15))
        delays = [s.get("delay_minutes", 0) for s in roster if s.get("delay_minutes", 0) > 0]
        avg_delay = float(sum(delays) / max(len(delays), 1)) if delays else 0.0

        features = {
            "staff_absence_count": absence_count,
            "late_checkin_count": late_count,
            "staffing_coverage_ratio": rule_eval["staffing_coverage_ratio"],
            "service_risk_count": rule_eval["service_risk_count"],
            "service_interruption_count": 1 if rule_eval["service_risk_count"] >= 2 else 0,
            "average_checkin_delay": avg_delay,
            "offline_duration": 18.0 if req.offline_mode else 0.0,
            "pending_sync_events": 3 if req.offline_mode else 0,
            "recent_alert_frequency": len(rule_eval["rule_violations"])
        }

        if req.override_features:
            features.update(req.override_features)

        # 3. Edge AI Model Inference
        ai_res = edge_model.predict(features, facility_id=req.facility_id)

        inference_record = {
            "inference_id": f"INF-{int(datetime.now().timestamp()*1000) % 100000}",
            "facility_id": req.facility_id,
            "timestamp": datetime.now().isoformat(),
            "mode": "EDGE",
            "model_version": ai_res["model_version"],
            "anomaly_score": ai_res["anomaly_score"],
            "status": ai_res["status"],
            "features": features,
            "sync_status": "PENDING" if req.offline_mode else "SYNCED",
            "top_contributing_factors": ai_res["top_contributing_factors"],
            "explanation": ai_res["explanation"]
        }

        # 4. Alert Fusion with Continuity Options & Critical Override
        fused_alerts = rule_engine.fuse_alerts(
            rule_result=rule_eval,
            edge_ai_result=ai_res,
            full_staff_pool=full_pool,
            facility_id=req.facility_id,
            offline_mode=req.offline_mode
        )

        return {
            "facility_id": req.facility_id,
            "offline_mode": req.offline_mode,
            "timestamp": datetime.now().isoformat(),
            "rule_evaluation": rule_eval,
            "edge_ai_inference": inference_record,
            "fused_alerts": fused_alerts,
            "staff_roster": roster,
            "full_staff_pool": full_pool
        }
    finally:
        db.close()

# --- Sync & Central Overview Endpoints ---

@app.post("/api/sync/batch")
def sync_batch(req: SyncBatchRequest):
    """
    Central Cloud Sync Receiver.
    Receives batched items queued during offline mode.
    Prioritizes critical alerts, deduplicates, and logs batch audit.
    """
    res = sync_processor.process_batch(req.dict())
    return res

@app.get("/api/staff/{facility_id}")
def get_staff(facility_id: str):
    db = SessionLocal()
    try:
        staff_rows = db.query(StaffRecord).filter(StaffRecord.facility_id == facility_id).all()
        return [
            {
                "staff_id": s.staff_id,
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "status": s.status,
                "scheduled_time": s.scheduled_time,
                "current_shift": s.current_shift,
                "checkin_time": s.checkin_time,
                "delay_minutes": s.delay_minutes,
                "leave_status": s.leave_status,
                "leave_approved": s.leave_approved,
                "leave_reason": s.leave_reason,
                "is_reserve": s.is_reserve,
                "qualified_services": s.qualified_services,
                "workload_hours": s.workload_hours
            }
            for s in staff_rows
        ]
    finally:
        db.close()

@app.post("/api/staff/update")
def update_staff(req: StaffUpdateRequest):
    db = SessionLocal()
    try:
        s = db.query(StaffRecord).filter(StaffRecord.staff_id == req.staff_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Staff not found")
        s.status = req.status
        if req.checkin_time:
            s.checkin_time = req.checkin_time
        if req.delay_minutes is not None:
            s.delay_minutes = req.delay_minutes
        db.commit()
        return {"status": "SUCCESS", "staff_id": s.staff_id, "updated_status": s.status}
    finally:
        db.close()

@app.get("/api/central/overview")
def get_central_overview():
    """
    Central Command Center Overview.
    Aggregates fleet status, synchronized inferences, active alerts,
    immutable attendance ledger, and continuity plans.
    """
    db = SessionLocal()
    try:
        facilities = db.query(FacilityRecord).all()
        inferences = db.query(InferenceRecord).order_by(InferenceRecord.timestamp.desc()).limit(15).all()
        alerts = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(15).all()
        batches = db.query(SyncBatchRecord).order_by(SyncBatchRecord.synced_at.desc()).limit(10).all()
        attendance_events = db.query(AttendanceEventRecord).order_by(AttendanceEventRecord.timestamp.desc()).limit(20).all()
        continuity_plans = db.query(StaffContinuityPlanRecord).order_by(StaffContinuityPlanRecord.timestamp.desc()).limit(10).all()

        total_fac = len(facilities)
        total_inferences = db.query(InferenceRecord).count()
        critical_alerts_count = db.query(AlertRecord).filter(AlertRecord.priority == "CRITICAL").count()

        parsed_inferences = []
        for inf in inferences:
            try:
                feat = json.loads(inf.features) if isinstance(inf.features, str) else inf.features
            except:
                feat = {}
            parsed_inferences.append({
                "inference_id": inf.inference_id,
                "facility_id": inf.facility_id,
                "timestamp": inf.timestamp,
                "mode": inf.mode,
                "model_version": inf.model_version,
                "anomaly_score": inf.anomaly_score,
                "status": inf.status,
                "features": feat,
                "sync_status": inf.sync_status,
                "synced_at": inf.synced_at.isoformat() if inf.synced_at else None
            })

        parsed_alerts = [
            {
                "alert_id": a.alert_id,
                "facility_id": a.facility_id,
                "timestamp": a.timestamp,
                "priority": a.priority,
                "service_id": a.service_id,
                "rule_violation": a.rule_violation,
                "ai_anomaly_score": a.ai_anomaly_score,
                "critical_override_active": a.critical_override_active,
                "message": a.message,
                "status": a.status,
                "action_taken": a.action_taken
            }
            for a in alerts
        ]

        parsed_batches = [
            {
                "batch_id": b.batch_id,
                "facility_id": b.facility_id,
                "synced_at": b.synced_at.isoformat() if b.synced_at else None,
                "record_count": b.record_count,
                "duration_ms": b.duration_ms,
                "status": b.status
            }
            for b in batches
        ]

        parsed_attendance = [
            {
                "event_id": e.event_id,
                "facility_id": e.facility_id,
                "staff_id": e.staff_id,
                "staff_name": e.staff_name,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "status_code": e.status_code,
                "device_id": e.device_id,
                "verification_method": e.verification_method,
                "proxy_risk_score": e.proxy_risk_score,
                "event_hash": e.event_hash
            }
            for e in attendance_events
        ]

        parsed_plans = [
            {
                "plan_id": p.plan_id,
                "facility_id": p.facility_id,
                "service_name": p.service_name,
                "unavailable_staff_name": p.unavailable_staff_name,
                "option_type": p.option_type,
                "assigned_staff_name": p.assigned_staff_name,
                "details": p.details,
                "status": p.status,
                "authorized_by": p.authorized_by,
                "authorized_at": p.authorized_at
            }
            for p in continuity_plans
        ]

        return {
            "metrics": {
                "total_facilities": total_fac,
                "online_facilities": sum(1 for f in facilities if f.status == "ONLINE"),
                "total_synced_inferences": total_inferences,
                "active_critical_alerts": critical_alerts_count,
                "total_attendance_events": len(attendance_events),
                "state": "Maharashtra Public Health Directorate",
                "district": "Pune Rural Health Circle"
            },
            "facilities": [
                {
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "district": f.district,
                    "status": f.status,
                    "last_sync": f.last_sync.isoformat() if f.last_sync else None,
                    "total_staff": f.total_staff,
                    "baseline_coverage": f.baseline_coverage
                }
                for f in facilities
            ],
            "recent_inferences": parsed_inferences,
            "recent_alerts": parsed_alerts,
            "recent_sync_batches": parsed_batches,
            "recent_attendance_events": parsed_attendance,
            "recent_continuity_plans": parsed_plans
        }
    finally:
        db.close()

# =========================================================================
# SYNVARA — HLTH04 ADVANCED RESEARCH & DESIGN ENDPOINTS
# =========================================================================

class CompositeScoringRequest(BaseModel):
    service_tier: int = 1
    services_impact_score: float = 1.0
    anomaly_score: float = 0.75
    unresolved_minutes: int = 15
    absenteeism_count_30d: int = 2
    has_stockout: bool = False
    is_emergency_unavailable: bool = False

@app.get("/api/synvara/role-substitution-matrix")
def get_role_substitution_matrix():
    """
    01 Staff Replacement: Pre-configured role-substitution rules matrix (WHO WISN grounded).
    """
    return rule_engine.get_role_substitution_matrix()

@app.get("/api/scoring/multi-phc-queue")
def get_multi_phc_alert_queue():
    """
    08 Enhanced Service Scoring Engine (v2) — Multi-PHC Alert Prioritization Queue.
    Demonstrates hard emergency override and composite priority formula across 4 PHCs.
    """
    return rule_engine.get_multi_phc_alert_queue()

@app.post("/api/scoring/composite-calculate")
def calculate_composite_score(req: CompositeScoringRequest):
    """
    Evaluates composite priority score formula for custom parameters.
    """
    return rule_engine.calculate_composite_priority_score(
        service_tier=req.service_tier,
        services_impact_score=req.services_impact_score,
        anomaly_score=req.anomaly_score,
        unresolved_minutes=req.unresolved_minutes,
        absenteeism_count_30d=req.absenteeism_count_30d,
        has_stockout=req.has_stockout,
        is_emergency_unavailable=req.is_emergency_unavailable
    )

@app.get("/api/synvara/field-research-plan")
def get_field_research_plan():
    """
    02 Ground-Level Field Research: 15-question validation matrix across Categories A, B, and C.
    """
    return rule_engine.get_field_research_plan()

@app.get("/api/synvara/attendance-integrity-matrix")
def get_attendance_integrity_matrix():
    """
    04 Attendance Integrity: Who can mark attendance authorization matrix & fraud prevention safeguards.
    """
    return rule_engine.get_attendance_integrity_matrix()

@app.get("/api/synvara/dpdp-privacy-spec")
def get_dpdp_privacy_spec():
    """
    05 Face Recognition Architecture & DPDP Act 2023 privacy compliance.
    """
    return rule_engine.get_dpdp_privacy_spec()

@app.get("/api/attendance/events-toggle/{facility_id}")
def get_attendance_events_toggle(facility_id: str, view_mode: str = "as_corrected"):
    """
    06 Immutable Attendance Records:
    Allows reports/dashboards to toggle between 'as_recorded' (raw unedited chain)
    and 'as_corrected' (supervisory approved operational state).
    """
    db = SessionLocal()
    try:
        events = db.query(AttendanceEventRecord).filter(
            AttendanceEventRecord.facility_id == facility_id
        ).order_by(AttendanceEventRecord.timestamp.desc()).all()

        corrections = db.query(CorrectionRequestRecord).filter(
            CorrectionRequestRecord.facility_id == facility_id,
            CorrectionRequestRecord.status == "APPROVED"
        ).all()
        corr_map = {c.original_event_id: c for c in corrections}

        result = []
        for e in events:
            has_corr = e.event_id in corr_map
            corr_obj = corr_map.get(e.event_id)

            if view_mode == "as_corrected" and has_corr:
                effective_status = corr_obj.proposed_status
                status_flag = f"CORRECTED ({corr_obj.proposed_status})"
            else:
                effective_status = e.status_code
                status_flag = "AS_RECORDED"

            result.append({
                "event_id": e.event_id,
                "staff_id": e.staff_id,
                "staff_name": e.staff_name,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "raw_status": e.status_code,
                "effective_status": effective_status,
                "status_flag": status_flag,
                "is_corrected": has_corr,
                "correction_id": corr_obj.correction_id if corr_obj else None,
                "correction_reason": corr_obj.reason if corr_obj else None,
                "verification_method": e.verification_method,
                "device_id": e.device_id,
                "previous_event_id": e.previous_event_id,
                "event_hash": e.event_hash
            })

        return {
            "facility_id": facility_id,
            "view_mode": view_mode,
            "total_events": len(result),
            "corrected_events_count": len(corrections),
            "events": result
        }
    finally:
        db.close()
