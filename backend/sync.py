"""
Sync Engine for Batch Synchronization from Offline Edge Devices to Central Cloud.
Implements priority ordering, idempotency / deduplication, append-only attendance validation,
and audit tracking.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .database import (
    SessionLocal,
    FacilityRecord,
    InferenceRecord,
    EventRecord,
    AlertRecord,
    SyncBatchRecord,
    AttendanceEventRecord,
    CorrectionRequestRecord,
    StaffContinuityPlanRecord,
    StaffRecord
)

class CentralSyncProcessor:
    def __init__(self):
        pass

    def process_batch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming offline sync payload.
        Priority order of processing:
        1. CRITICAL Alerts & Emergency Continuity Actions (Immediate clinical safety)
        2. Immutable Attendance Events & Corrections (Audit trail integrity)
        3. Edge AI Inferences
        4. General operational events
        """
        facility_id = payload.get("facility_id", "PHC-004")
        batch_id = payload.get("batch_id", f"BATCH-{int(datetime.now().timestamp()*1000)}")
        inferences = payload.get("inferences", [])
        events = payload.get("events", [])
        alerts = payload.get("alerts", [])
        attendance_events = payload.get("attendance_events", [])
        corrections = payload.get("corrections", [])
        continuity_plans = payload.get("continuity_plans", [])

        db: Session = SessionLocal()
        synced_counts = {
            "alerts": 0,
            "attendance_events": 0,
            "corrections": 0,
            "continuity_plans": 0,
            "inferences": 0,
            "events": 0,
            "duplicates_skipped": 0
        }
        start_time = datetime.now()

        try:
            # Update facility status and last sync
            fac = db.query(FacilityRecord).filter(FacilityRecord.facility_id == facility_id).first()
            if fac:
                fac.last_sync = datetime.utcnow()
                fac.status = "ONLINE"

            # 1. Process Alerts with priority ordering (CRITICAL first)
            sorted_alerts = sorted(alerts, key=lambda a: 0 if a.get("priority") == "CRITICAL" else 1)
            for a in sorted_alerts:
                aid = a.get("alert_id")
                existing = db.query(AlertRecord).filter(AlertRecord.alert_id == aid).first()
                if not existing:
                    new_alert = AlertRecord(
                        alert_id=aid,
                        facility_id=facility_id,
                        timestamp=a.get("timestamp", datetime.now().isoformat()),
                        priority=a.get("priority", "HIGH"),
                        service_id=a.get("service_id", "general"),
                        rule_violation=a.get("rule_violation"),
                        ai_anomaly_score=float(a.get("ai_anomaly_score", 0.0)),
                        critical_override_active=bool(a.get("critical_override_active", False)),
                        message=a.get("message", ""),
                        status=a.get("status", "ACTIVE"),
                        action_taken=a.get("action_taken", ""),
                        synced_at=datetime.utcnow()
                    )
                    db.add(new_alert)
                    synced_counts["alerts"] += 1
                else:
                    if a.get("action_taken") and not existing.action_taken:
                        existing.action_taken = a.get("action_taken")
                        existing.status = a.get("status", "ACTIONED")
                    synced_counts["duplicates_skipped"] += 1

            # 2. Process Immutable Attendance Events (Append-only)
            for att in attendance_events:
                eid = att.get("event_id")
                existing = db.query(AttendanceEventRecord).filter(AttendanceEventRecord.event_id == eid).first()
                if not existing:
                    new_att = AttendanceEventRecord(
                        event_id=eid,
                        facility_id=facility_id,
                        staff_id=att.get("staff_id", "UNKNOWN"),
                        staff_name=att.get("staff_name", "Unknown Staff"),
                        timestamp=att.get("timestamp", datetime.now().isoformat()),
                        event_type=att.get("event_type", "ATTENDANCE_CHECKIN"),
                        status_code=att.get("status_code", "PRESENT"),
                        device_id=att.get("device_id", "EDGE-CAM-PHC004-A"),
                        verification_method=att.get("verification_method", "FACE_EDGE"),
                        proxy_risk_score=float(att.get("proxy_risk_score", 0.0)),
                        proxy_risk_level=att.get("proxy_risk_level", "LOW"),
                        created_by=att.get("created_by", "EDGE_FACE_AI"),
                        sync_status="SYNCED",
                        previous_event_id=att.get("previous_event_id"),
                        event_hash=att.get("event_hash"),
                        notes=att.get("notes"),
                        synced_at=datetime.utcnow()
                    )
                    db.add(new_att)
                    synced_counts["attendance_events"] += 1

                    # Update staff record status in cloud mirror
                    staff_rec = db.query(StaffRecord).filter(StaffRecord.staff_id == att.get("staff_id")).first()
                    if staff_rec:
                        if att.get("event_type") == "ATTENDANCE_CHECKIN":
                            staff_rec.status = att.get("status_code", "PRESENT")
                            time_only = att.get("timestamp", "").split("T")[-1][:5]
                            staff_rec.checkin_time = time_only or "09:00"
                        elif att.get("event_type") == "REPLACEMENT_ASSIGNED":
                            staff_rec.status = "COVERED_ABSENCE"
                else:
                    synced_counts["duplicates_skipped"] += 1

            # 3. Process Correction Requests
            for cor in corrections:
                cid = cor.get("correction_id")
                existing = db.query(CorrectionRequestRecord).filter(CorrectionRequestRecord.correction_id == cid).first()
                if not existing:
                    new_cor = CorrectionRequestRecord(
                        correction_id=cid,
                        original_event_id=cor.get("original_event_id", ""),
                        facility_id=facility_id,
                        staff_id=cor.get("staff_id", ""),
                        staff_name=cor.get("staff_name", ""),
                        requested_by=cor.get("requested_by", "Staff"),
                        requested_at=cor.get("requested_at", datetime.now().isoformat()),
                        reason=cor.get("reason", ""),
                        proposed_status=cor.get("proposed_status", ""),
                        status=cor.get("status", "PENDING"),
                        reviewed_by=cor.get("reviewed_by"),
                        reviewed_at=cor.get("reviewed_at"),
                        admin_notes=cor.get("admin_notes")
                    )
                    db.add(new_cor)
                    synced_counts["corrections"] += 1
                else:
                    synced_counts["duplicates_skipped"] += 1

            # 4. Process Staff Continuity Plans
            for plan in continuity_plans:
                pid = plan.get("plan_id")
                existing = db.query(StaffContinuityPlanRecord).filter(StaffContinuityPlanRecord.plan_id == pid).first()
                if not existing:
                    new_plan = StaffContinuityPlanRecord(
                        plan_id=pid,
                        facility_id=facility_id,
                        service_id=plan.get("service_id", ""),
                        service_name=plan.get("service_name", ""),
                        unavailable_staff_id=plan.get("unavailable_staff_id", ""),
                        unavailable_staff_name=plan.get("unavailable_staff_name", ""),
                        option_type=plan.get("option_type", "RELIEF_ASSIGNMENT"),
                        assigned_staff_id=plan.get("assigned_staff_id"),
                        assigned_staff_name=plan.get("assigned_staff_name"),
                        details=plan.get("details", ""),
                        status=plan.get("status", "AUTHORIZED"),
                        authorized_by=plan.get("authorized_by", "Medical Superintendent"),
                        authorized_at=plan.get("authorized_at", datetime.now().isoformat()),
                        timestamp=plan.get("timestamp", datetime.now().isoformat())
                    )
                    db.add(new_plan)
                    synced_counts["continuity_plans"] += 1
                else:
                    synced_counts["duplicates_skipped"] += 1

            # 5. Process Edge AI Inferences
            for inf in inferences:
                inf_id = inf.get("inference_id")
                existing = db.query(InferenceRecord).filter(InferenceRecord.inference_id == inf_id).first()
                if not existing:
                    features_str = json.dumps(inf.get("features", {})) if isinstance(inf.get("features"), dict) else str(inf.get("features", "{}"))
                    new_inf = InferenceRecord(
                        inference_id=inf_id,
                        facility_id=facility_id,
                        timestamp=inf.get("timestamp", datetime.now().isoformat()),
                        mode=inf.get("mode", "EDGE"),
                        model_version=inf.get("model_version", "edge-anomaly-v1"),
                        anomaly_score=float(inf.get("anomaly_score", 0.0)),
                        status=inf.get("status", "NORMAL"),
                        features=features_str,
                        sync_status="SYNCED",
                        synced_at=datetime.utcnow()
                    )
                    db.add(new_inf)
                    synced_counts["inferences"] += 1
                else:
                    synced_counts["duplicates_skipped"] += 1

            # 6. Process Events
            for ev in events:
                ev_id = ev.get("event_id")
                existing = db.query(EventRecord).filter(EventRecord.event_id == ev_id).first()
                if not existing:
                    payload_str = json.dumps(ev.get("payload", {})) if isinstance(ev.get("payload"), dict) else str(ev.get("payload", "{}"))
                    new_ev = EventRecord(
                        event_id=ev_id,
                        facility_id=facility_id,
                        timestamp=ev.get("timestamp", datetime.now().isoformat()),
                        event_type=ev.get("event_type", "GENERAL"),
                        payload=payload_str,
                        priority=ev.get("priority", "NORMAL"),
                        sync_status="SYNCED",
                        synced_at=datetime.utcnow()
                    )
                    db.add(new_ev)
                    synced_counts["events"] += 1
                else:
                    synced_counts["duplicates_skipped"] += 1

            # Record Sync Batch Audit
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            total_synced = (
                synced_counts["alerts"] +
                synced_counts["attendance_events"] +
                synced_counts["corrections"] +
                synced_counts["continuity_plans"] +
                synced_counts["inferences"] +
                synced_counts["events"]
            )
            batch_record = SyncBatchRecord(
                batch_id=batch_id,
                facility_id=facility_id,
                synced_at=datetime.utcnow(),
                record_count=total_synced,
                duration_ms=duration_ms,
                status="SUCCESS"
            )
            db.add(batch_record)
            db.commit()

            return {
                "status": "SUCCESS",
                "batch_id": batch_id,
                "facility_id": facility_id,
                "synced_counts": synced_counts,
                "total_records_ingested": total_synced,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "ERROR",
                "batch_id": batch_id,
                "facility_id": facility_id,
                "error": str(e)
            }
        finally:
            db.close()

sync_processor = CentralSyncProcessor()
