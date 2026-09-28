/**
 * PHC Opsense - Multilingual Localization Engine (i18n)
 * Authentic medical and operational translations for:
 * 1. English (EN)
 * 2. Marathi (मराठी - MR)
 * 3. Hindi (हिन्दी - HI)
 */

const I18N_TRANSLATIONS = {
  en: {
    // Brand & Header
    project_name: "SYNVARA",
    project_tagline: "Intelligent Operational Monitoring for Primary Healthcare",
    facility_name: "PHC Pune (Shirwal)",
    facility_subtitle: "Primary Health Centre • Pune Rural Health Circle • NHM Maharashtra",
    edge_node: "Health Center",
    online: "Online",
    offline: "Offline",
    syncing: "Syncing",
    pending_sync: "Pending Sync",

    // Roles
    role_mo: "Medical Officer",
    role_staff: "PHC Staff",
    role_dho: "District Officer",
    role_admin: "System Admin",

    // Tabs
    tab_dashboard: "Dashboard",
    tab_attendance: "Attendance",
    tab_staff: "Staff & Schedule",
    tab_services: "Services",
    tab_alerts: "Alerts",
    tab_leave: "Leave",
    tab_analytics: "Analytics",
    tab_district: "District Fleet",
    tab_settings: "Settings",

    // Top 4 Summary Cards
    summary_services: "Services Available",
    summary_staff: "Staff Present",
    summary_alerts: "Active Alerts",
    summary_critical: "Critical Issues",

    // Sections
    services_title: "Service Availability",
    services_subtitle: "Key PHC Services & Staffing Requirements",
    staff_title: "Today's Staff Roster",
    staff_subtitle: "Attendance, Active Shift & Assigned Service",
    alerts_title: "Active Operational Alerts",
    alerts_subtitle: "Actionable Operational Alerts Requiring Attention",
    edge_ai_title: "Operational Anomaly Risk",
    edge_ai_subtitle: "Edge AI Anomaly Detection",

    // Diagnostic Fields
    what_happened: "WHAT HAPPENED",
    why_happened: "WHY IT HAPPENED",
    operational_impact: "OPERATIONAL IMPACT",
    available_action: "AVAILABLE ACTION",
    coverage_options: "AVAILABLE COVERAGE",
    recommended_action: "RECOMMENDED ACTION",

    // Statuses
    status_available: "Available",
    status_at_risk: "At Risk",
    status_limited: "Limited",
    status_present: "Present",
    status_late: "Late",
    status_approved_leave: "Approved Leave",
    status_absent: "Absent",
    status_off_duty: "Off Duty",

    // Buttons & Actions
    btn_view_details: "View Details",
    btn_view_issue: "View Issue",
    btn_view_all_staff: "View All Staff",
    btn_assign_replacement: "Assign Replacement",
    btn_request_approval: "Request Approval",
    btn_escalate: "Escalate",
    btn_resolve: "Resolve",
    btn_dismiss: "Dismiss with Reason",
    btn_record_checkin: "Record Face Check-In",
    btn_request_correction: "Request Correction",

    // Landing & Auth
    nav_features: "Features",
    nav_tech: "Technology",
    nav_roles: "Roles",
    nav_arch: "Architecture",
    nav_impact: "Impact",
    btn_portal: "Launch Portal",
    btn_signin: "Sign In",
    btn_signout: "Sign Out",
    btn_home: "Home",
    btn_demo: "Instant Demo",

    // Offline Banner
    offline_banner_title: "OFFLINE AUTONOMOUS MODE ACTIVE:",
    offline_banner_desc: "Internet disconnected. Clinic operations, Edge AI, and staff attendance continue running locally on this device.",
    zero_cloud: "Zero Cloud Dependency"
  },

  mr: {
    // Brand & Header
    project_name: "SYNVARA",
    project_tagline: "प्राथमिक आरोग्य केंद्रांसाठी बुद्धिमान परिचालन नियंत्रण प्रणाली",
    facility_name: "प्राथमिक आरोग्य केंद्र पुणे (शिरवळ)",
    facility_subtitle: "प्राथमिक आरोग्य केंद्र • पुणे ग्रामीण आरोग्य मंडळ • राष्ट्रीय आरोग्य अभियान महाराष्ट्र",
    edge_node: "आरोग्य केंद्र",
    online: "ऑनलाइन",
    offline: "ऑफलाइन",
    syncing: "सिंक सुरू",
    pending_sync: "प्रलंबित सिंक",

    // Roles
    role_mo: "वैद्यकीय अधिकारी",
    role_staff: "आरोग्य कर्मचारी",
    role_dho: "जिल्हा आरोग्य अधिकारी",
    role_admin: "प्रणाली व्यवस्थापक",

    // Tabs
    tab_dashboard: "डॅशबोर्ड",
    tab_attendance: "हजेरी",
    tab_staff: "कर्मचारी व वेळापत्रक",
    tab_services: "आरोग्य सेवा",
    tab_alerts: "अलर्ट",
    tab_leave: "रजा व्यवस्थापन",
    tab_analytics: "विश्लेषण",
    tab_district: "जिल्हा केंद्र",
    tab_settings: "सेटिंग्ज",

    // Top 4 Summary Cards
    summary_services: "उपलब्ध सेवा",
    summary_staff: "हजर कर्मचारी",
    summary_alerts: "सक्रिय अलर्ट",
    summary_critical: "गंभीर समस्या",

    // Sections
    services_title: "आरोग्य सेवा उपलब्धता",
    services_subtitle: "महत्त्वाच्या क्लिनिकल सेवा व आवश्यक कर्मचारी संख्या",
    staff_title: "आजचा कर्मचारी हजेरी तक्ता",
    staff_subtitle: "हजेरी स्थिती, ड्युटी वेळ व नेमून दिलेली सेवा",
    alerts_title: "सक्रिय परिचालन अलर्ट",
    alerts_subtitle: "त्वरित लक्ष देण्याची गरज असलेले महत्त्वाचे अलर्ट",
    edge_ai_title: "परिचालन विसंगती जोखीम",
    edge_ai_subtitle: "स्थानिक एज एआय विसंगती शोधक",

    // Diagnostic Fields
    what_happened: "काय घडले?",
    why_happened: "का घडले?",
    operational_impact: "सेवेवर परिणाम",
    available_action: "उपलब्ध कृती",
    coverage_options: "उपलब्ध पर्यायी कर्मचारी",
    recommended_action: "शिफारस केलेली कृती",

    // Statuses
    status_available: "सुरू (उपलब्ध)",
    status_at_risk: "धोक्यात (At Risk)",
    status_limited: "मर्यादित",
    status_present: "हजर",
    status_late: "उशीर",
    status_approved_leave: "अधिकृत रजा",
    status_absent: "गैरहजर",
    status_off_duty: "ड्युटीबाहेर",

    // Buttons & Actions
    btn_view_details: "तपशील पहा",
    btn_view_issue: "समस्या पहा",
    btn_view_all_staff: "सर्व कर्मचारी पहा",
    btn_assign_replacement: "पर्यायी कर्मचारी नियुक्त करा",
    btn_request_approval: "मंजुरी विनंती करा",
    btn_escalate: "वरिष्ठांकडे पाठवा",
    btn_resolve: "निवारण झाले",
    btn_dismiss: "कारणासह बंद करा",
    btn_record_checkin: "चेहरा हजेरी नोंदवा",
    btn_request_correction: "दुरुस्ती विनंती करा",

    // Landing & Auth
    nav_features: "वैशिष्ट्ये",
    nav_tech: "तंत्रज्ञान",
    nav_roles: "भूमिका",
    nav_arch: "आर्किटेक्चर",
    nav_impact: "प्रभाव",
    btn_portal: "पोर्टल सुरू करा",
    btn_signin: "लॉगिन करा",
    btn_signout: "बाहेर पडा",
    btn_home: "मुख्यपृष्ठ",
    btn_demo: "डेमो सुरू करा",

    // Offline Banner
    offline_banner_title: "ऑफलाइन स्वायत्त मोड सक्रिय:",
    offline_banner_desc: "इंटरनेट खंडित झाले आहे. स्थानिक एज एआय आणि कर्मचारी हजेरी या उपकरणावर स्वायत्तपणे सुरू आहे.",
    zero_cloud: "क्लाउडवर शून्य अवलंबित्व"
  },

  hi: {
    // Brand & Header
    project_name: "SYNVARA",
    project_tagline: "प्राथमिक स्वास्थ्य केंद्रों हेतु बुद्धिमान परिचालन निगरानी प्रणाली",
    facility_name: "प्राथमिक स्वास्थ्य केंद्र पुणे (शिरवल)",
    facility_subtitle: "प्राथमिक स्वास्थ्य केंद्र • पुणे ग्रामीण स्वास्थ्य वृत्त • राष्ट्रीय स्वास्थ्य मिशन महाराष्ट्र",
    edge_node: "स्वास्थ्य केंद्र",
    online: "ऑनलाइन",
    offline: "ऑफलाइन",
    syncing: "सिंकिंग जारी",
    pending_sync: "लंबित सिंक",

    // Roles
    role_mo: "चिकित्सा अधिकारी",
    role_staff: "स्वास्थ्य स्टाफ",
    role_dho: "जिला स्वास्थ्य अधिकारी",
    role_admin: "सिस्टम व्यवस्थापक",

    // Tabs
    tab_dashboard: "डैशबोर्ड",
    tab_attendance: "उपस्थिति",
    tab_staff: "स्टाफ व शेड्यूल",
    tab_services: "सेवाएं",
    tab_alerts: "अलर्ट",
    tab_leave: "अवकाश",
    tab_analytics: "एनालिटिक्स",
    tab_district: "जिला फ्लीट",
    tab_settings: "सेटिंग्स",

    // Top 4 Summary Cards
    summary_services: "उपलब्ध सेवाएं",
    summary_staff: "उपस्थित स्टाफ",
    summary_alerts: "सक्रिय अलर्ट",
    summary_critical: "गंभीर समस्याएं",

    // Sections
    services_title: "सेवा उपलब्धता",
    services_subtitle: "महत्वपूर्ण प्राथमिक सेवाएं एवं आवश्यक स्टाफ आवश्यकता",
    staff_title: "आज का स्टाफ रोस्टर",
    staff_subtitle: "उपस्थिति, वर्तमान शिफ्ट एवं आवंटित सेवा",
    alerts_title: "सक्रिय परिचालन अलर्ट",
    alerts_subtitle: "शीघ्र ध्यान आकर्षित करने वाले महत्वपूर्ण अलर्ट",
    edge_ai_title: "परिचालन असामान्यता जोखिम",
    edge_ai_subtitle: "स्थानीय एज एआई विश्लेषण",

    // Diagnostic Fields
    what_happened: "क्या हुआ?",
    why_happened: "क्यों हुआ?",
    operational_impact: "सेवा पर प्रभाव",
    available_action: "उपलब्ध कार्रवाई",
    coverage_options: "उपलब्ध वैकल्पिक स्टाफ",
    recommended_action: "अनुशंसित कार्रवाई",

    // Statuses
    status_available: "उपलब्ध",
    status_at_risk: "जोखिम में (At Risk)",
    status_limited: "सीमित",
    status_present: "उपस्थित",
    status_late: "देरी से",
    status_approved_leave: "स्वीकृत अवकाश",
    status_absent: "अनुपस्थित",
    status_off_duty: "ड्यूटी समाप्त",

    // Buttons & Actions
    btn_view_details: "विवरण देखें",
    btn_view_issue: "समस्या देखें",
    btn_view_all_staff: "सभी स्टाफ देखें",
    btn_assign_replacement: "वैकल्पिक स्टाफ नियुक्त करें",
    btn_request_approval: "अनुमोदन अनुरोध भेजें",
    btn_escalate: "उच्चाधिकारियों को भेजें",
    btn_resolve: "समाधान करें",
    btn_dismiss: "कारण सहित बंद करें",
    btn_record_checkin: "फेस अटेंडेंस दर्ज करें",
    btn_request_correction: "सुधार अनुरोध दर्ज करें",

    // Landing & Auth
    nav_features: "विशेषताएं",
    nav_tech: "प्रौद्योगिकी",
    nav_roles: "भूमिकाएं",
    nav_arch: "आर्किटेक्चर",
    nav_impact: "प्रभाव",
    btn_portal: "पोर्टल खोलें",
    btn_signin: "लॉग इन करें",
    btn_signout: "लॉग आउट",
    btn_home: "होम",
    btn_demo: "डेमो खोलें",

    // Offline Banner
    offline_banner_title: "ऑफलाइन स्वायत्त मोड सक्रिय:",
    offline_banner_desc: "इंटरनेट संपर्क टूट चुका है। क्लिनिक संचालन, एज एआई और स्टाफ उपस्थिति स्थानीय रूप से जारी है।",
    zero_cloud: "क्लाउड पर शून्य निर्भरता"
  }
};

class I18nEngine {
  constructor() {
    this.currentLang = localStorage.getItem("opsense_lang") || "en";
  }

  setLanguage(lang) {
    if (I18N_TRANSLATIONS[lang]) {
      this.currentLang = lang;
      localStorage.setItem("opsense_lang", lang);
      this.applyTranslations();
      document.querySelectorAll(".lang-btn").forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
      });
    }
  }

  t(key, fallback = "") {
    const dict = I18N_TRANSLATIONS[this.currentLang] || I18N_TRANSLATIONS.en;
    return dict[key] || I18N_TRANSLATIONS.en[key] || fallback || key;
  }

  applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      const trans = this.t(key);
      if (trans) {
        if (el.tagName === "INPUT" && el.getAttribute("placeholder")) {
          el.setAttribute("placeholder", trans);
        } else {
          el.textContent = trans;
        }
      }
    });
  }
}

const i18n = new I18nEngine();
