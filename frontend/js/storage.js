/**
 * PHC Edge AI - Local Event Store & IndexedDB Engine (Version 3)
 * Provides persistent offline storage for:
 * 1. Inferences (Edge AI 2 Operational Anomaly)
 * 2. Immutable Append-Only Attendance Event Ledger
 * 3. Correction Request Audit Trail
 * 4. Staff Continuity & Overtime Authorization Plans
 * 5. Fused Clinical Alerts & Priority Sync Queue
 */

class EdgeStorage {
  constructor(dbName = "PHCEdgeDB", version = 3) {
    this.dbName = dbName;
    this.version = version;
    this.db = null;
    this.isReady = this.init();
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onupgradeneeded = (e) => {
        const db = e.target.result;

        // 1. Inferences store
        if (!db.objectStoreNames.contains("inferences")) {
          const infStore = db.createObjectStore("inferences", { keyPath: "inference_id" });
          infStore.createIndex("sync_status", "sync_status", { unique: false });
          infStore.createIndex("timestamp", "timestamp", { unique: false });
        }

        // 2. Operational Events store
        if (!db.objectStoreNames.contains("events")) {
          const evStore = db.createObjectStore("events", { keyPath: "event_id" });
          evStore.createIndex("sync_status", "sync_status", { unique: false });
          evStore.createIndex("priority", "priority", { unique: false });
          evStore.createIndex("timestamp", "timestamp", { unique: false });
        }

        // 3. Alerts store
        if (!db.objectStoreNames.contains("alerts")) {
          const altStore = db.createObjectStore("alerts", { keyPath: "alert_id" });
          altStore.createIndex("priority", "priority", { unique: false });
          altStore.createIndex("sync_status", "sync_status", { unique: false });
        }

        // 4. Immutable Attendance Events Ledger (Append-only)
        if (!db.objectStoreNames.contains("attendance_events")) {
          const attStore = db.createObjectStore("attendance_events", { keyPath: "event_id" });
          attStore.createIndex("staff_id", "staff_id", { unique: false });
          attStore.createIndex("timestamp", "timestamp", { unique: false });
          attStore.createIndex("sync_status", "sync_status", { unique: false });
        }

        // 5. Attendance Correction Requests store
        if (!db.objectStoreNames.contains("corrections")) {
          const corrStore = db.createObjectStore("corrections", { keyPath: "correction_id" });
          corrStore.createIndex("status", "status", { unique: false });
          corrStore.createIndex("sync_status", "sync_status", { unique: false });
        }

        // 6. Staff Continuity & Overtime Plans store
        if (!db.objectStoreNames.contains("continuity_plans")) {
          const contStore = db.createObjectStore("continuity_plans", { keyPath: "plan_id" });
          contStore.createIndex("service_id", "service_id", { unique: false });
          contStore.createIndex("sync_status", "sync_status", { unique: false });
        }

        // Local state
        if (!db.objectStoreNames.contains("app_state")) {
          db.createObjectStore("app_state", { keyPath: "key" });
        }
      };

      request.onsuccess = (e) => {
        this.db = e.target.result;
        resolve(this.db);
      };

      request.onerror = (e) => {
        console.error("IndexedDB initialization error:", e);
        reject(e);
      };
    });
  }

  async _tx(storeName, mode = "readonly") {
    await this.isReady;
    return this.db.transaction([storeName], mode).objectStore(storeName);
  }

  // --- Inferences ---
  async saveInference(inferenceRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("inferences", "readwrite");
        const req = store.put(inferenceRecord);
        req.onsuccess = () => resolve(inferenceRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllInferences() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("inferences", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Immutable Attendance Events (Append-only) ---
  async saveAttendanceEvent(eventRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("attendance_events", "readwrite");
        const req = store.put(eventRecord);
        req.onsuccess = () => resolve(eventRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllAttendanceEvents() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("attendance_events", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Correction Requests ---
  async saveCorrection(corrRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("corrections", "readwrite");
        const req = store.put(corrRecord);
        req.onsuccess = () => resolve(corrRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllCorrections() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("corrections", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Staff Continuity Plans ---
  async saveContinuityPlan(planRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("continuity_plans", "readwrite");
        const req = store.put(planRecord);
        req.onsuccess = () => resolve(planRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllContinuityPlans() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("continuity_plans", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Events ---
  async saveEvent(eventRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("events", "readwrite");
        const req = store.put(eventRecord);
        req.onsuccess = () => resolve(eventRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllEvents() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("events", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Alerts ---
  async saveAlert(alertRecord) {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("alerts", "readwrite");
        const req = store.put(alertRecord);
        req.onsuccess = () => resolve(alertRecord);
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  async getAllAlerts() {
    await this.isReady;
    return new Promise(async (resolve, reject) => {
      try {
        const store = await this._tx("alerts", "readonly");
        const req = store.getAll();
        req.onsuccess = () => resolve((req.result || []).reverse());
        req.onerror = (e) => reject(e);
      } catch (err) {
        reject(err);
      }
    });
  }

  // --- Priority-Based Sync Queue ---
  async getPendingSyncPayload(facilityId = "PHC-004") {
    await this.isReady;
    const allInfs = await this.getAllInferences();
    const allEvs = await this.getAllEvents();
    const allAlts = await this.getAllAlerts();
    const allAtts = await this.getAllAttendanceEvents();
    const allCorrs = await this.getAllCorrections();
    const allPlans = await this.getAllContinuityPlans();

    const pendingInfs = allInfs.filter(i => i.sync_status === "PENDING");
    const pendingEvs = allEvs.filter(e => e.sync_status === "PENDING");
    const pendingAlts = allAlts.filter(a => a.sync_status === "PENDING" || !a.sync_status);
    const pendingAtts = allAtts.filter(a => a.sync_status === "PENDING");
    const pendingCorrs = allCorrs.filter(c => c.sync_status === "PENDING");
    const pendingPlans = allPlans.filter(p => p.sync_status === "PENDING");

    // Priority ordering: CRITICAL Alerts & Continuity first
    pendingAlts.sort((a, b) => (a.priority === "CRITICAL" ? -1 : 1));

    return {
      facility_id: facilityId,
      batch_id: `BATCH-${Date.now()}`,
      alerts: pendingAlts,
      attendance_events: pendingAtts,
      corrections: pendingCorrs,
      continuity_plans: pendingPlans,
      inferences: pendingInfs,
      events: pendingEvs,
      total_pending: (
        pendingInfs.length +
        pendingEvs.length +
        pendingAlts.length +
        pendingAtts.length +
        pendingCorrs.length +
        pendingPlans.length
      )
    };
  }

  async markAsSynced(inferences = [], events = [], alerts = [], attendance_events = [], corrections = [], continuity_plans = []) {
    await this.isReady;
    const now = new Date().toISOString();

    const markStore = async (storeName, items) => {
      if (items && items.length > 0) {
        const store = await this._tx(storeName, "readwrite");
        for (const item of items) {
          item.sync_status = "SYNCED";
          item.synced_at = now;
          store.put(item);
        }
      }
    };

    await markStore("inferences", inferences);
    await markStore("events", events);
    await markStore("alerts", alerts);
    await markStore("attendance_events", attendance_events);
    await markStore("corrections", corrections);
    await markStore("continuity_plans", continuity_plans);
  }

  async clearAll() {
    await this.isReady;
    for (const name of ["inferences", "events", "alerts", "attendance_events", "corrections", "continuity_plans"]) {
      try {
        const store = await this._tx(name, "readwrite");
        store.clear();
      } catch (e) {
        console.warn(`Could not clear store ${name}:`, e);
      }
    }
  }
}

// Global storage singleton
const edgeStorage = new EdgeStorage();
