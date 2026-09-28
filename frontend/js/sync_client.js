/**
 * PHC Edge AI - Priority Sync Client (Version 2)
 * Manages priority-based synchronization from local IndexedDB queue to Central Cloud.
 * Priority Order:
 * 1. CRITICAL Alerts & Continuity Action Plans
 * 2. Immutable Attendance Events & Corrections
 * 3. Edge AI Inferences
 * 4. General Operational Events
 */

class SyncClient {
  constructor(storage = edgeStorage) {
    this.storage = storage;
    this.isOnline = true;
    this.isSyncing = false;
    this.listeners = [];
  }

  setOnline(online) {
    const wasOffline = !this.isOnline;
    this.isOnline = !!online;
    this._notifyListeners({ type: "CONNECTIVITY_CHANGE", isOnline: this.isOnline });

    // Auto-trigger sync when connectivity returns
    if (wasOffline && this.isOnline) {
      this.triggerSync();
    }
  }

  onSyncUpdate(callback) {
    this.listeners.push(callback);
  }

  _notifyListeners(data) {
    for (const cb of this.listeners) {
      try { cb(data); } catch (e) { console.error("Listener error", e); }
    }
  }

  async getPendingCount() {
    try {
      const payload = await this.storage.getPendingSyncPayload();
      return payload.total_pending;
    } catch (e) {
      return 0;
    }
  }

  async triggerSync(facilityId = "PHC-004") {
    if (!this.isOnline) {
      return { status: "OFFLINE", message: "Cannot sync: System is in OFFLINE mode." };
    }
    if (this.isSyncing) {
      return { status: "BUSY", message: "Sync operation already in progress." };
    }

    this.isSyncing = true;
    this._notifyListeners({ type: "SYNC_START" });

    try {
      const payload = await this.storage.getPendingSyncPayload(facilityId);

      if (payload.total_pending === 0) {
        this.isSyncing = false;
        this._notifyListeners({ type: "SYNC_COMPLETE", count: 0 });
        return { status: "SUCCESS", count: 0, message: "Queue is empty. All records synchronized." };
      }

      const resp = await fetch("/api/sync/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) {
        throw new Error(`Sync server responded with ${resp.status}`);
      }

      const syncResult = await resp.json();

      // Mark all categories as synced in local IndexedDB
      await this.storage.markAsSynced(
        payload.inferences,
        payload.events,
        payload.alerts,
        payload.attendance_events,
        payload.corrections,
        payload.continuity_plans
      );

      this.isSyncing = false;
      this._notifyListeners({ 
        type: "SYNC_COMPLETE", 
        count: payload.total_pending, 
        result: syncResult 
      });

      return {
        status: "SUCCESS",
        count: payload.total_pending,
        syncResult: syncResult
      };
    } catch (err) {
      this.isSyncing = false;
      this._notifyListeners({ type: "SYNC_ERROR", error: err.message });
      console.error("Sync error:", err);
      return { status: "ERROR", error: err.message };
    }
  }
}

// Global sync client singleton
const syncClient = new SyncClient();
