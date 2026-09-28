"""
Central Database & Storage Models using SQLite (SQLAlchemy).
Maintains central cloud records, append-only attendance event ledger,
cross-facility sync store, and fleet audit log.
"""

import os
import json
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "central_cloud.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FacilityRecord(Base):
    __tablename__ = "facilities"
    facility_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    district = Column(String(100), default="Pune Rural")
    state = Column(String(100), default="Maharashtra")
    status = Column(String(20), default="ONLINE")
    last_sync = Column(DateTime, default=datetime.utcnow)
    baseline_coverage = Column(Float, default=0.88)
    total_staff = Column(Integer, default=10)

class StaffRecord(Base):
    __tablename__ = "staff_roster"
    staff_id = Column(String(50), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # DOCTOR, NURSE, ANM, PHARMACIST
    department = Column(String(100), nullable=False)
    scheduled_time = Column(String(20), default="09:00")
    current_shift = Column(String(50), default="09:00–17:00")
    status = Column(String(50), default="SCHEDULED")  # SCHEDULED, PRESENT, CHECKED_IN, LATE, ABSENT, APPROVED_LEAVE, UNAUTHORIZED_ABSENCE, REPLACED, COVERED_ABSENCE, OFF_DUTY
    checkin_time = Column(String(50), nullable=True)
    delay_minutes = Column(Integer, default=0)
    leave_status = Column(String(50), default="NONE")  # NONE, APPROVED_LEAVE, CASUAL_LEAVE, MEDICAL_LEAVE
    leave_approved = Column(Boolean, default=False)
    leave_reason = Column(String(100), nullable=True)
    is_reserve = Column(Boolean, default=False)  # IPHS 15% leave/training reserve pool
    qualified_services = Column(Text, default="emergency,maternity_labour,outpatient_opd")
    workload_hours = Column(Float, default=8.0)
    # Step 1, 2, 5: Offline Biometric Face Registry fields
    face_embedding = Column(Text, nullable=True)  # JSON-serialized numerical vector (ArcFace 512-D)
    face_consent = Column(Boolean, default=False)  # Explicit consent confirmation
    face_enrolled_at = Column(String(50), nullable=True)  # Timestamp of enrollment
    face_image_path = Column(String(255), nullable=True)  # Optional local reference

class AttendanceEventRecord(Base):
    """
    Append-Only Immutable Attendance Event Model.
    Rule: Attendance once marked cannot be edited or deleted.
    Every event links to previous_event_id forming an unbroken cryptographic audit chain.
    """
    __tablename__ = "attendance_events"
    event_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    staff_id = Column(String(50), nullable=False)
    staff_name = Column(String(100), nullable=False)
    timestamp = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)  # ATTENDANCE_CHECKIN, ATTENDANCE_CHECKOUT, LEAVE_APPROVED, CORRECTION_REQUESTED, CORRECTION_APPROVED, REPLACEMENT_ASSIGNED, OVERTIME_APPROVED
    status_code = Column(String(50), default="PRESENT")  # PRESENT, LATE, ABSENT, APPROVED_LEAVE, UNAUTHORIZED_ABSENCE, REPLACED, COVERED_ABSENCE
    device_id = Column(String(100), default="EDGE-CAM-PHC004-A")
    verification_method = Column(String(50), default="FACE_EDGE")  # FACE_EDGE, MANUAL_AUTHORIZED, GEOFENCE_AUTO
    proxy_risk_score = Column(Float, default=0.0)  # 0.0 (clean) to 1.0 (fraud/mismatch)
    proxy_risk_level = Column(String(20), default="LOW")  # LOW, ELEVATED, IDENTITY_MISMATCH
    created_by = Column(String(100), default="EDGE_FACE_AI")
    sync_status = Column(String(20), default="SYNCED")  # PENDING, SYNCED
    previous_event_id = Column(String(100), nullable=True)
    event_hash = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)

class CorrectionRequestRecord(Base):
    """
    Attendance Correction Request Audit Trail.
    Original events remain permanently untouched; corrections append a reviewed resolution.
    """
    __tablename__ = "attendance_corrections"
    correction_id = Column(String(100), primary_key=True)
    original_event_id = Column(String(100), nullable=False)
    facility_id = Column(String(50), nullable=False)
    staff_id = Column(String(50), nullable=False)
    staff_name = Column(String(100), nullable=False)
    requested_by = Column(String(100), nullable=False)
    requested_at = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    proposed_status = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(String(50), nullable=True)
    admin_notes = Column(Text, nullable=True)

class StaffContinuityPlanRecord(Base):
    """
    Staff Replacement / Overtime Authorization Records.
    Decision-Support: AI recommends continuity options, Admin must authorize.
    """
    __tablename__ = "staff_continuity_plans"
    plan_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    service_id = Column(String(50), nullable=False)
    service_name = Column(String(100), nullable=False)
    unavailable_staff_id = Column(String(50), nullable=False)
    unavailable_staff_name = Column(String(100), nullable=False)
    option_type = Column(String(50), nullable=False)  # RELIEF_ASSIGNMENT, OVERTIME_REQUEST, ESCALATION_REFERRAL
    assigned_staff_id = Column(String(50), nullable=True)
    assigned_staff_name = Column(String(100), nullable=True)
    details = Column(Text, nullable=False)
    status = Column(String(50), default="AUTHORIZED")  # RECOMMENDED, AUTHORIZED, REJECTED
    authorized_by = Column(String(100), nullable=False)
    authorized_at = Column(String(50), nullable=False)
    timestamp = Column(String(50), nullable=False)

class InferenceRecord(Base):
    __tablename__ = "inferences"
    inference_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    timestamp = Column(String(50), nullable=False)
    mode = Column(String(20), default="EDGE")
    model_version = Column(String(50), default="edge-anomaly-v1")
    anomaly_score = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)  # NORMAL, ELEVATED, UNUSUAL, CRITICAL
    features = Column(Text, nullable=False)  # JSON string
    sync_status = Column(String(20), default="SYNCED")
    synced_at = Column(DateTime, default=datetime.utcnow)

class EventRecord(Base):
    __tablename__ = "events"
    event_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    timestamp = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)  # JSON
    priority = Column(String(20), default="NORMAL")
    sync_status = Column(String(20), default="SYNCED")
    synced_at = Column(DateTime, default=datetime.utcnow)

class AlertRecord(Base):
    __tablename__ = "alerts"
    alert_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    timestamp = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False)
    service_id = Column(String(50), nullable=False)
    rule_violation = Column(Text, nullable=True)
    ai_anomaly_score = Column(Float, default=0.0)
    critical_override_active = Column(Boolean, default=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="ACTIVE")
    action_taken = Column(Text, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)

class SyncBatchRecord(Base):
    __tablename__ = "sync_batches"
    batch_id = Column(String(100), primary_key=True)
    facility_id = Column(String(50), nullable=False)
    synced_at = Column(DateTime, default=datetime.utcnow)
    record_count = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")

def compute_event_hash(event_id: str, staff_id: str, timestamp: str, event_type: str, prev_id: str) -> str:
    content = f"{event_id}|{staff_id}|{timestamp}|{event_type}|{prev_id or 'GENESIS'}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed default facilities if empty
    if not db.query(FacilityRecord).first():
        facilities = [
            FacilityRecord(facility_id="PHC-004", name="PHC Shirwal", district="Satara / Pune Rural", state="Maharashtra", status="ONLINE", total_staff=10),
            FacilityRecord(facility_id="PHC-001", name="PHC Khed", district="Pune Rural", state="Maharashtra", status="ONLINE", total_staff=8),
            FacilityRecord(facility_id="PHC-002", name="PHC Baramati", district="Pune Rural", state="Maharashtra", status="ONLINE", total_staff=9),
            FacilityRecord(facility_id="PHC-003", name="PHC Junnar", district="Pune Rural", state="Maharashtra", status="ONLINE", total_staff=7)
        ]
        db.add_all(facilities)

        # Seed staff for PHC-004 including Active + Reserve Staff (15% IPHS leave reserve)
        staff_members = [
            # Active Emergency & Trauma Shift (09:00 - 17:00)
            StaffRecord(
                staff_id="STF-001", facility_id="PHC-004", name="Dr. Rajesh Kulkarni", role="DOCTOR",
                department="Emergency & Trauma Care", scheduled_time="09:00", current_shift="09:00–17:00",
                status="SCHEDULED", qualified_services="emergency,outpatient_opd", workload_hours=8.0
            ),
            StaffRecord(
                staff_id="STF-002", facility_id="PHC-004", name="Nurse Sunita Patil", role="NURSE",
                department="Emergency & Trauma Care", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:52", qualified_services="emergency,maternity_labour", workload_hours=8.0
            ),
            # Maternity & Labour Room
            StaffRecord(
                staff_id="STF-003", facility_id="PHC-004", name="Dr. Ananya Sharma", role="DOCTOR",
                department="Maternity & Labour Room", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:55", qualified_services="maternity_labour,emergency", workload_hours=8.0
            ),
            StaffRecord(
                staff_id="STF-004", facility_id="PHC-004", name="ANM Priya Jadhav", role="ANM",
                department="Maternity & Labour Room", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:58", qualified_services="maternity_labour", workload_hours=8.0
            ),
            # General OPD
            StaffRecord(
                staff_id="STF-005", facility_id="PHC-004", name="Dr. Vikram Deshmukh", role="DOCTOR",
                department="General Outpatient (OPD)", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:50", qualified_services="outpatient_opd,emergency", workload_hours=8.0
            ),
            # Pharmacy & Cold Chain
            StaffRecord(
                staff_id="STF-006", facility_id="PHC-004", name="Pharmacist Suresh Shinde", role="PHARMACIST",
                department="Pharmacy & Cold Chain", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:48", qualified_services="pharmacy_cold_chain", workload_hours=8.0
            ),
            # --- IPHS 2022 15% Leave & Relief Staff Pool ---
            StaffRecord(
                staff_id="STF-007", facility_id="PHC-004", name="Dr. Rahul Mehra", role="DOCTOR",
                department="Emergency & Trauma Care (Relief)", scheduled_time="14:00", current_shift="14:00–18:00 (Relief)",
                status="OFF_DUTY", is_reserve=True, qualified_services="emergency,outpatient_opd", workload_hours=4.0
            ),
            StaffRecord(
                staff_id="STF-008", facility_id="PHC-004", name="Dr. Sneha Kulkarni", role="DOCTOR",
                department="Inpatient Ward", scheduled_time="09:00", current_shift="09:00–17:00",
                status="CHECKED_IN", checkin_time="08:45", is_reserve=False, qualified_services="emergency,inpatient", workload_hours=8.0
            ),
            StaffRecord(
                staff_id="STF-009", facility_id="PHC-004", name="Dr. Sameer Patil", role="DOCTOR",
                department="General Outpatient (OPD)", scheduled_time="09:00", current_shift="09:00–17:00",
                status="APPROVED_LEAVE", leave_status="APPROVED_LEAVE", leave_approved=True,
                leave_reason="Annual Training / Sanctioned Leave (IPHS Leave Reserve)", is_reserve=False,
                qualified_services="outpatient_opd", workload_hours=0.0
            ),
            StaffRecord(
                staff_id="STF-010", facility_id="PHC-004", name="Nurse Kavita Shinde", role="NURSE",
                department="Nursing Reserve Pool", scheduled_time="12:00", current_shift="On-Call / Reserve",
                status="OFF_DUTY", is_reserve=True, qualified_services="emergency,maternity_labour", workload_hours=0.0
            )
        ]
        db.add_all(staff_members)

        # Seed initial immutable attendance events
        prev_hash = "GENESIS-PHC004"
        events_to_seed = [
            ("ATT-EV-001", "STF-002", "Nurse Sunita Patil", "08:52:14", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.02, "LOW"),
            ("ATT-EV-002", "STF-003", "Dr. Ananya Sharma", "08:55:09", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.01, "LOW"),
            ("ATT-EV-003", "STF-004", "ANM Priya Jadhav", "08:58:32", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.03, "LOW"),
            ("ATT-EV-004", "STF-005", "Dr. Vikram Deshmukh", "08:50:45", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.02, "LOW"),
            ("ATT-EV-005", "STF-006", "Pharmacist Suresh Shinde", "08:48:19", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.04, "LOW"),
            ("ATT-EV-006", "STF-008", "Dr. Sneha Kulkarni", "08:45:00", "ATTENDANCE_CHECKIN", "PRESENT", "EDGE-CAM-PHC004-A", "FACE_EDGE", 0.01, "LOW"),
            ("ATT-EV-007", "STF-009", "Dr. Sameer Patil", "08:00:00", "LEAVE_APPROVED", "APPROVED_LEAVE", "ADMIN-PORTAL", "MANUAL_AUTHORIZED", 0.0, "LOW")
        ]
        
        last_id = None
        for eid, sid, sname, t_str, etype, scode, dev, vmethod, prisk, plevel in events_to_seed:
            full_t = f"{datetime.now().strftime('%Y-%m-%d')}T{t_str}"
            ehash = compute_event_hash(eid, sid, full_t, etype, last_id or prev_hash)
            ev = AttendanceEventRecord(
                event_id=eid,
                facility_id="PHC-004",
                staff_id=sid,
                staff_name=sname,
                timestamp=full_t,
                event_type=etype,
                status_code=scode,
                device_id=dev,
                verification_method=vmethod,
                proxy_risk_score=prisk,
                proxy_risk_level=plevel,
                created_by="EDGE_FACE_AI" if vmethod == "FACE_EDGE" else "ADMIN",
                sync_status="SYNCED",
                previous_event_id=last_id or prev_hash,
                event_hash=ehash,
                notes="Standard verified entry"
            )
            db.add(ev)
            last_id = eid

        db.commit()
    db.close()
