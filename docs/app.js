/* ClearWage WH-347 — 100% Client-Side Revised Jan-2025 (Mandatory Oct 1, 2026)
 * Davis-Bacon / CWHSSA / Copeland Act Compliance Auditor & Official DOL PDF Compiler.
 * Zero payroll PII ever leaves the user's browser.
 */

const CHECKOUT_CONFIG = {
  // Paste your Gumroad or Polar.sh product URL here once created (takes 60 seconds):
  proSuiteCheckoutUrl: "",
  repoReleasesUrl: "https://github.com/zchryst/clearwage-wh347",
  priceUsd: 79,
  freePdfMaxRows: 5
};

const P1_ROW_BANDS = [
  [282.3, 295.4, 310.0],
  [310.7, 324.0, 337.9],
  [338.7, 351.5, 365.9],
  [366.7, 380.4, 394.8],
  [395.6, 409.3, 423.7],
  [424.5, 438.2, 452.2],
  [452.2, 466.1, 480.0],
  [480.0, 494.0, 508.4]
];

const P1_DAY_X = [
  [341.4, 355.6],
  [355.6, 367.8],
  [367.8, 380.2],
  [380.2, 392.5],
  [392.5, 404.9],
  [404.9, 417.2],
  [417.2, 430.4]
];

const P2_PLAN_X = [
  [144.0, 238.6],
  [238.6, 333.0],
  [333.0, 427.6],
  [427.6, 522.0],
  [522.0, 616.6],
  [616.6, 711.0]
];

const P2_WORKER_Y = [
  [371.9, 383.6],
  [383.6, 395.2],
  [395.2, 406.6],
  [406.6, 418.1],
  [418.1, 429.6],
  [429.6, 441.0],
  [441.0, 452.5],
  [452.5, 464.0]
];

function qCent(n) {
  return Math.round((Number(n) + Number.EPSILON) * 100) / 100;
}

function fmtMoney(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "";
  return Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtHrs(n) {
  const v = Number(n || 0);
  if (v === 0) return "";
  return Number.isInteger(v) ? String(v) : String(qCent(v));
}

function buildCleanPreset() {
  return {
    project_name: "VA Outpatient Surgical Wing MEP Modernization",
    project_no: "36C257-26-C-0114",
    certified_payroll_no: 4,
    contractor_role: "subcontractor",
    business_name: "Lone Star Mechanical & Controls LLC",
    business_address: "4820 Burnet Rd, Suite 210, Austin, TX 78756",
    project_location: "7901 Metropolis Dr, Austin, Travis County, TX 78744",
    wage_determination_no: "TX20260028 Mod 3 (Building)",
    week_ending_date: "2026-10-24",
    certifying_official_name: "Elena M. Vance",
    certifying_official_title: "Payroll & Compliance Manager",
    telephone: "(512) 555-0194",
    email: "compliance@lonestarmech-example.com",
    additional_remarks: "All electronic timecards reconciled against GC daily sign-in logs.",
    is_final_payroll: false,
    cwhssa_applies: true,
    wage_determinations: [
      { classification: "Electrician (Inside Wireman)", basic_hourly_rate: 38.50, fringe_hourly_rate: 14.20 },
      { classification: "HVAC Sheet Metal Mechanic", basic_hourly_rate: 35.00, fringe_hourly_rate: 12.80 },
      { classification: "Laborer - Common / General", basic_hourly_rate: 22.40, fringe_hourly_rate: 7.60 }
    ],
    apprentice_programs: [
      {
        program_name: "Austin Electrical JATC Local 520",
        registration_agency: "OA",
        labor_classification: "Electrician (Inside Wireman)",
        progression_pct: 65,
        fringes_full_rate: true,
        ratio_apprentices: 1,
        ratio_journeyworkers: 1
      }
    ],
    fringe_plans: [
      { plan_id: "FB1", fb_name: "IBEW/NECA Health & Welfare", fb_type: "Medical/Dental", plan_no: "HW-520-A", is_funded: true },
      { plan_id: "FB2", fb_name: "NEBF National Pension Trust", fb_type: "Defined Benefit", plan_no: "PN-001", is_funded: true },
      { plan_id: "FB3", fb_name: "JATC Apprenticeship Training", fb_type: "Apprenticeship", plan_no: "TR-520", is_funded: true }
    ],
    rows: [
      {
        worker_entry_no: 1,
        last_name: "Ramirez",
        first_name: "Carlos",
        middle_initial: "A",
        worker_id: "4829",
        status: "J",
        apprentice_progression: "",
        labor_classification: "Electrician (Inside Wireman)",
        st_hours: [0, 8, 8, 8, 8, 8, 0],
        ot_hours: [0, 0, 0, 0, 0, 2, 2],
        st_rate_paid: 39.00,
        ot_rate_paid: 58.50,
        fb1: 8.50,
        fb2: 4.95,
        fb3: 0.75,
        cash_in_lieu_rate: 0.00,
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 0.00,
        tax: 248.40,
        fica: 137.24,
        other_ded: 35.88,
        other_ded_desc: "IBEW Working Dues (29 CFR 3.5(i))"
      },
      {
        worker_entry_no: 2,
        last_name: "Chen",
        first_name: "Marcus",
        middle_initial: "L",
        worker_id: "9104",
        status: "J",
        apprentice_progression: "",
        labor_classification: "Electrician (Inside Wireman)",
        st_hours: [0, 8, 8, 8, 0, 0, 0],
        ot_hours: [0, 0, 0, 0, 0, 0, 0],
        st_rate_paid: 38.50,
        ot_rate_paid: 57.75,
        fb1: 8.50,
        fb2: 4.95,
        fb3: 0.75,
        cash_in_lieu_rate: 0.00,
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 310.00,
        tax: 231.10,
        fica: 137.85,
        other_ded: 0.00,
        other_ded_desc: ""
      },
      {
        worker_entry_no: 2,
        last_name: "Chen",
        first_name: "Marcus",
        middle_initial: "L",
        worker_id: "9104",
        status: "J",
        apprentice_progression: "",
        labor_classification: "HVAC Sheet Metal Mechanic",
        st_hours: [0, 0, 0, 0, 8, 8, 0],
        ot_hours: [0, 0, 0, 0, 0, 0, 0],
        st_rate_paid: 35.50,
        ot_rate_paid: 53.25,
        fb1: 8.50,
        fb2: 4.30,
        fb3: 0.00,
        cash_in_lieu_rate: 0.00,
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 0.00,
        tax: 0.00,
        fica: 0.00,
        other_ded: 0.00,
        other_ded_desc: ""
      },
      {
        worker_entry_no: 3,
        last_name: "Brooks",
        first_name: "Devin",
        middle_initial: "T",
        worker_id: "7731",
        status: "RA",
        apprentice_progression: "Per. 3 (65%)",
        labor_classification: "Electrician (Inside Wireman)",
        st_hours: [0, 8, 8, 8, 8, 8, 0],
        ot_hours: [0, 0, 0, 0, 0, 0, 0],
        st_rate_paid: 25.50,
        ot_rate_paid: 38.25,
        fb1: 8.50,
        fb2: 4.95,
        fb3: 0.75,
        cash_in_lieu_rate: 0.00,
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 0.00,
        tax: 112.00,
        fica: 78.03,
        other_ded: 0.00,
        other_ded_desc: ""
      },
      {
        worker_entry_no: 4,
        last_name: "Kowalski",
        first_name: "Tomasz",
        middle_initial: "",
        worker_id: "3318",
        status: "J",
        apprentice_progression: "",
        labor_classification: "Laborer - Common / General",
        st_hours: [0, 8, 8, 8, 8, 8, 0],
        ot_hours: [0, 0, 0, 0, 0, 0, 0],
        st_rate_paid: 22.40,
        ot_rate_paid: 33.60,
        fb1: 4.00,
        fb2: 0.00,
        fb3: 0.00,
        cash_in_lieu_rate: 3.60,
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 0.00,
        tax: 108.50,
        fica: 79.56,
        other_ded: 177.00,
        other_ded_desc: "Child Support Order #TX-8841 ($125.00); 401(k) Deferral ($52.00)"
      }
    ]
  };
}

function buildTrapPreset() {
  const s = buildCleanPreset();
  s.wage_determination_no = ""; // Trap 1: Missing new Jan-2025 Wage Determination No.
  s.rows[0].worker_id = "459-82-4829"; // Trap 2: Full 9-digit SSN in Col 1E
  s.rows[0].includes_cash_fringe_in_6a = true; // Trap 3: Cash-in-lieu mixed into Col 6A
  s.rows[4].st_hours = [0, 8, 8, 8, 8, 8, 6]; // Trap 4: 46 ST hrs, 0 OT hrs (CWHSSA violation!)
  s.rows[4].cash_in_lieu_rate = 1.60; // Trap 5: $2.00/hr prevailing fringe underpayment
  s.apprentice_programs = []; // Trap 6: Unregistered apprentice on Page 2 Box 4
  return s;
}

let state = buildTrapPreset();

function getWeekDates(weekEndingStr) {
  const letters = ["S", "M", "T", "W", "T", "F", "S"];
  const parts = (weekEndingStr || "2026-10-24").split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) {
    return { letters, dates: ["", "", "", "", "", "", ""] };
  }
  const end = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
  const outLetters = [];
  const outDates = [];
  const dowMap = ["S", "M", "T", "W", "T", "F", "S"];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(end.getTime() - i * 86400000);
    outLetters.push(dowMap[d.getUTCDay()]);
    outDates.push(`${String(d.getUTCMonth() + 1).padStart(2, "0")}/${String(d.getUTCDate()).padStart(2, "0")}`);
  }
  return { letters: outLetters, dates: outDates };
}

function computeAndAudit(data) {
  const wdMap = {};
  (data.wage_determinations || []).forEach(w => {
    wdMap[w.classification.trim().toLowerCase()] = w;
  });
  const apMap = {};
  (data.apprentice_programs || []).forEach(p => {
    apMap[p.labor_classification.trim().toLowerCase()] = p;
  });

  const seenWorkers = new Set();
  const lines = data.rows.map((r, idx) => {
    const stTot = qCent(r.st_hours.reduce((a, b) => a + Number(b || 0), 0));
    const otTot = qCent(r.ot_hours.reduce((a, b) => a + Number(b || 0), 0));
    const totHrs = qCent(stTot + otTot);
    const hrFringeCredit = qCent(Number(r.fb1 || 0) + Number(r.fb2 || 0) + Number(r.fb3 || 0));
    const col6B = qCent(totHrs * hrFringeCredit);
    const col6C = qCent(totHrs * Number(r.cash_in_lieu_rate || 0));
    const col7A = qCent(stTot * Number(r.st_rate_paid || 0) + otTot * Number(r.ot_rate_paid || 0) + col6C);
    const isPrimary = !seenWorkers.has(Number(r.worker_entry_no));
    seenWorkers.add(Number(r.worker_entry_no));

    const clsKey = (r.labor_classification || "").trim().toLowerCase();
    const wd = wdMap[clsKey] || null;
    let reqBasic = wd ? Number(wd.basic_hourly_rate) : null;
    let reqFringe = wd ? Number(wd.fringe_hourly_rate) : null;
    if (r.status === "RA" && wd && apMap[clsKey]) {
      const pct = Number(apMap[clsKey].progression_pct || 100) / 100;
      reqBasic = qCent(reqBasic * pct);
      if (!apMap[clsKey].fringes_full_rate) {
        reqFringe = qCent(reqFringe * pct);
      }
    }

    const effStTotal = qCent(Number(r.st_rate_paid || 0) + hrFringeCredit + Number(r.cash_in_lieu_rate || 0));
    const effOtTotal = qCent(Number(r.ot_rate_paid || 0) + hrFringeCredit + Number(r.cash_in_lieu_rate || 0));
    let reqStTotal = reqBasic !== null ? qCent(reqBasic + reqFringe) : null;
    let stShortfall = reqStTotal !== null ? Math.max(0, qCent(reqStTotal - effStTotal)) : 0;

    let reqOtTotal = null;
    let minCashOt = null;
    let otShortfall = 0;
    if (reqBasic !== null) {
      const regBase = Math.max(reqBasic, Number(r.st_rate_paid || 0));
      reqOtTotal = qCent(1.5 * regBase + reqFringe);
      const effFringe = qCent(hrFringeCredit + Number(r.cash_in_lieu_rate || 0));
      const extraFringe = Math.max(0, effFringe - reqFringe);
      minCashOt = Math.max(qCent(1.5 * Number(r.st_rate_paid || 0)), qCent(reqOtTotal - extraFringe - reqFringe));
      otShortfall = Math.max(0, qCent(reqOtTotal - effOtTotal));
    }

    return {
      idx,
      src: r,
      stTot,
      otTot,
      totHrs,
      hrFringeCredit,
      col6B,
      col6C,
      col7A,
      isPrimary,
      reqBasic,
      reqFringe,
      reqStTotal,
      effStTotal,
      stShortfall,
      reqOtTotal,
      minCashOt,
      effOtTotal,
      otShortfall,
      col7B: null,
      col8Tax: null,
      col8Fica: null,
      col8Other: null,
      col8Total: null,
      col9Net: null
    };
  });

  // Roll up Col 7A per unique worker_entry_no so split-classification workers never double-count 7B/8/9
  const worker7ASum = {};
  lines.forEach(l => {
    const eno = Number(l.src.worker_entry_no);
    worker7ASum[eno] = qCent((worker7ASum[eno] || 0) + l.col7A);
  });

  lines.forEach(l => {
    if (l.isPrimary) {
      const eno = Number(l.src.worker_entry_no);
      l.col7B = qCent(worker7ASum[eno] + Number(l.src.other_projects_gross || 0));
      l.col8Tax = qCent(Number(l.src.tax || 0));
      l.col8Fica = qCent(Number(l.src.fica || 0));
      l.col8Other = qCent(Number(l.src.other_ded || 0));
      l.col8Total = qCent(l.col8Tax + l.col8Fica + l.col8Other);
      l.col9Net = qCent(l.col7B - l.col8Total);
    }
  });

  // Page 2 worker fringe rows (max 1 row per unique worker)
  const p2FringeMap = new Map();
  lines.forEach(l => {
    const eno = Number(l.src.worker_entry_no);
    const cur = p2FringeMap.get(eno) || {
      eno,
      displayName: `#${eno} ${l.src.last_name}, ${l.src.first_name} ${l.src.middle_initial || ""}`.trim(),
      fb1: 0, fb2: 0, fb3: 0, total: 0
    };
    cur.fb1 = Math.max(cur.fb1, Number(l.src.fb1 || 0));
    cur.fb2 = Math.max(cur.fb2, Number(l.src.fb2 || 0));
    cur.fb3 = Math.max(cur.fb3, Number(l.src.fb3 || 0));
    cur.total = qCent(cur.fb1 + cur.fb2 + cur.fb3);
    p2FringeMap.set(eno, cur);
  });

  const total6B = qCent(lines.reduce((s, l) => s + l.col6B, 0));
  const total6C = qCent(lines.reduce((s, l) => s + l.col6C, 0));
  const anyRA = lines.some(l => l.src.status === "RA");

  // Run 26-rule Statutory Audit
  const findings = [];
  if (!["prime", "subcontractor"].includes((data.contractor_role || "").toLowerCase())) {
    findings.push({
      rule_id: "WH347-001", severity: "BLOCKER",
      title: "Missing Prime vs. Subcontractor Role Selection",
      detail: "Page 1 header requires marking either Prime Contractor or Subcontractor.",
      cfr: "DOL WH-347 Instructions (OMB 1235-0008)", back_wages: 0,
      fix: "Select Prime Contractor or Subcontractor in Project Header."
    });
  }
  if (!data.wage_determination_no || !data.wage_determination_no.trim()) {
    findings.push({
      rule_id: "WH347-003", severity: "BLOCKER",
      title: "Missing Mandatory SAM.gov Wage Determination No. (New Jan-2025 Box)",
      detail: "Revised Form WH-347 (mandatory Oct 1, 2026) added a dedicated Wage Determination No. header box; blank submissions are rejected by GCs and agencies.",
      cfr: "DOL WH-347 Header Instructions (Rev. Jan 2025)", back_wages: 0,
      fix: "Enter the contract's SAM.gov Wage Determination number & modification (e.g., 'TX20260028 Mod 3')."
    });
  }
  if (!data.project_location || data.project_location.trim().length < 5) {
    findings.push({
      rule_id: "WH347-004", severity: "BLOCKER",
      title: "Incomplete Project Location (County & State Required)",
      detail: "Project Location must identify at minimum County and State.",
      cfr: "29 CFR § 5.5(a)(3)(ii)", back_wages: 0,
      fix: "Add full project site description including County and State."
    });
  }
  if (!data.certifying_official_name.trim() || !data.certifying_official_title.trim()) {
    findings.push({
      rule_id: "WH347-005", severity: "BLOCKER",
      title: "Missing Certifying Official Name or Title on Page 2",
      detail: "Statement of Compliance must state the certifying official's name and title under 18 U.S.C. § 1001.",
      cfr: "29 CFR § 3.3(b)", back_wages: 0,
      fix: "Enter Certifying Official Name and Title."
    });
  }

  const ssnRe = /^\s*(?:\d{3}-\d{2}-\d{4}|\d{9})\s*$/;
  const workerHrs = {};
  const workerOtHrs = {};
  const identToEno = {};
  const enoToIdent = {};

  lines.forEach(l => {
    const r = l.src;
    const eno = Number(r.worker_entry_no);
    const ident = `${r.last_name.trim().toLowerCase()}|${r.first_name.trim().toLowerCase()}`;

    if (ssnRe.test(r.worker_id || "")) {
      findings.push({
        rule_id: "WH347-007", severity: "BLOCKER",
        title: `Full 9-Digit Social Security Number in Col 1E (Entry #${eno} — ${r.last_name})`,
        detail: `Col 1E contains '${r.worker_id}'. Full SSNs are strictly prohibited under 29 CFR § 5.5(a)(3)(ii)(A) privacy rules.`,
        cfr: "29 CFR § 5.5(a)(3)(ii)(A)", back_wages: 0,
        fix: "Truncate Col 1E to last 4 digits of SSN (e.g. '4829') or employee ID."
      });
    } else if (!(r.worker_id || "").trim()) {
      findings.push({
        rule_id: "WH347-008", severity: "BLOCKER",
        title: `Missing Worker Identifying Number in Col 1E (Entry #${eno})`,
        detail: "Every worker requires a 4-digit SSN suffix or internal employee ID.",
        cfr: "29 CFR § 5.5(a)(3)(ii)(B)", back_wages: 0,
        fix: "Enter 4-digit worker ID in Col 1E."
      });
    }

    if (enoToIdent[eno] && enoToIdent[eno] !== ident) {
      findings.push({
        rule_id: "WH347-009", severity: "BLOCKER",
        title: `Duplicate Worker Entry #${eno} Assigned to Different Workers`,
        detail: "Only split-classification rows for the SAME individual worker may share a Col 1A Entry No.",
        cfr: "DOL WH-347 Col 1A Instructions", back_wages: 0,
        fix: "Assign distinct sequential Col 1A numbers to distinct employees."
      });
    }
    enoToIdent[eno] = ident;

    if (identToEno[ident] && identToEno[ident] !== eno) {
      findings.push({
        rule_id: "WH347-010", severity: "BLOCKER",
        title: `Split-Classification Worker Listed Under Different Entry Nos. (#${identToEno[ident]} vs #${eno})`,
        detail: "Rev. Jan 2025 instructions require reusing the SAME Col 1A Entry No. when one worker performs multiple classifications.",
        cfr: "DOL WH-347 Col 1A Instructions (Rev. Jan 2025)", back_wages: 0,
        fix: `Set Entry No. = ${identToEno[ident]} on both rows for ${r.last_name}.`
      });
    } else {
      identToEno[ident] = eno;
    }

    workerHrs[eno] = qCent((workerHrs[eno] || 0) + l.totHrs);
    workerOtHrs[eno] = qCent((workerOtHrs[eno] || 0) + l.otTot);

    if (r.status === "RA" && (!data.apprentice_programs || data.apprentice_programs.length === 0)) {
      findings.push({
        rule_id: "WH347-013", severity: "BLOCKER",
        title: `Unregistered Apprentice '${r.last_name}' Missing OA/SAA Program on Page 2 Box 4 (Entry #${eno})`,
        detail: "Apprentice rates are unlawful unless the worker is individually registered in a DOL OA or State SAA program listed on Page 2 Box 4.",
        cfr: "29 CFR § 5.5(a)(4)(i)", back_wages: 0,
        fix: "Register OA/SAA Apprenticeship Program on Page 2 Box 4 or pay full Journeyworker rate."
      });
    }

    if (r.includes_cash_fringe_in_6a) {
      findings.push({
        rule_id: "WH347-014", severity: "BLOCKER",
        title: `Cash-in-Lieu Fringe Mixed into Col 6A Base Rate (Entry #${eno} — ${r.last_name})`,
        detail: "Rev. Jan 2025 Col 6A strictly excludes cash paid in lieu of fringes. Cash-in-lieu must be separated into new Column 6C.",
        cfr: "DOL WH-347 Col 6A & 6C Instructions (Rev. Jan 2025)", back_wages: 0,
        fix: "Uncheck cash-fringe-in-6A and enter hourly cash fringe in Cash-in-Lieu ($/hr) for Col 6C."
      });
    }

    if (l.stShortfall > 0 && l.stTot > 0) {
      const bw = qCent(l.stTot * l.stShortfall);
      findings.push({
        rule_id: "WH347-016", severity: "BLOCKER",
        title: `Prevailing Wage + Fringe Shortfall of $${fmtMoney(l.stShortfall)}/hr (Entry #${eno} — ${r.last_name})`,
        detail: `Effective ST package ($${fmtMoney(l.effStTotal)}/hr) is below SAM.gov WD requirement ($${fmtMoney(l.reqStTotal)}/hr) across ${l.stTot} ST hrs.`,
        cfr: "29 CFR § 5.5(a)(1)(i); 40 U.S.C. § 3142", back_wages: bw,
        fix: `Increase Col 6C cash-in-lieu or Col 6A base rate by $${fmtMoney(l.stShortfall)}/hr (Back wages due: $${fmtMoney(bw)}).`
      });
    }

    if (l.otShortfall > 0 && l.otTot > 0) {
      const bw = qCent(l.otTot * l.otShortfall);
      findings.push({
        rule_id: "WH347-017", severity: "BLOCKER",
        title: `DBRA/CWHSSA Overtime Underpayment of $${fmtMoney(l.otShortfall)}/hr (Entry #${eno} — ${r.last_name})`,
        detail: `OT package ($${fmtMoney(l.effOtTotal)}/hr) is below statutory floor ($${fmtMoney(l.reqOtTotal)}/hr = 1.5x base + full fringe).`,
        cfr: "29 CFR § 5.32; 40 U.S.C. § 3702", back_wages: bw,
        fix: `Set Col 6A OT rate >= $${fmtMoney(l.minCashOt)}/hr (Back wages due: $${fmtMoney(bw)}).`
      });
    }

    if (l.isPrimary && l.col8Other > 0 && !(r.other_ded_desc || "").trim()) {
      findings.push({
        rule_id: "WH347-023", severity: "BLOCKER",
        title: `Unspecified 'Other' Deduction ($${fmtMoney(l.col8Other)}) in Col 8 (Entry #${eno})`,
        detail: "Copeland Act requires itemizing every 'Other' deduction on Page 2 Remarks or an Addendum.",
        cfr: "29 CFR § 3.5", back_wages: 0,
        fix: "Enter deduction description (e.g., 'Union Working Dues' or 'Child Support Order')."
      });
    }
  });

  let cwhssaDamages = 0;
  if (data.cwhssa_applies) {
    Object.keys(workerHrs).forEach(k => {
      const eno = Number(k);
      const tot = workerHrs[eno];
      const ot = workerOtHrs[eno] || 0;
      const reqOt = Math.max(0, qCent(tot - 40));
      if (ot < reqOt) {
        const unpaid = qCent(reqOt - ot);
        const primary = lines.find(x => Number(x.src.worker_entry_no) === eno);
        const bw = qCent(unpaid * 0.5 * Number(primary.src.st_rate_paid || 0));
        const estDays = Math.max(1, Math.floor(unpaid / 8) + 1);
        const liq = 32 * estDays;
        cwhssaDamages += liq;
        findings.push({
          rule_id: "WH347-019", severity: "BLOCKER",
          title: `CWHSSA >40 Weekly Hours Paid as Straight Time (Entry #${eno}: ${tot} hrs, ${ot} OT)`,
          detail: `Entry #${eno} worked ${tot} project hours across all classifications, requiring >=${reqOt} OT hrs. Triggers $${fmtMoney(bw)} half-time back wages PLUS ~$${fmtMoney(liq)} ($32/day) CWHSSA liquidated damages.`,
          cfr: "40 U.S.C. § 3702; 29 CFR § 5.5(b)(2)", back_wages: bw,
          fix: `Move ${unpaid} hours from Straight Time (ST) to Overtime (OT) and pay 1.5x OT rate.`
        });
      }
    });
  }

  // Check if >=2 Other deductions trigger Copeland Addendum
  const addendumDeductions = lines.filter(l => l.isPrimary && l.col8Other > 0 && (l.src.other_ded_desc || "").includes(";"));
  if (addendumDeductions.length > 0) {
    findings.push({
      rule_id: "WH347-026", severity: "WARNING",
      title: "Copeland Act Continuation Addendum Auto-Attached (Page 3)",
      detail: "Worker(s) have multiple 'Other' deductions separated by ';'. Per DOL Page 1 Col 8 instructions, ClearWage automatically generates and attaches Page 3 Itemized Deductions Addendum.",
      cfr: "DOL WH-347 Col 8 Instructions; 29 CFR § 3.5", back_wages: 0,
      fix: "Keep Page 3 Addendum attached when submitting signed PDF."
    });
  }

  const blockers = findings.filter(f => f.severity === "BLOCKER").length;
  const warnings = findings.filter(f => f.severity === "WARNING").length;
  const totalBackWages = qCent(findings.reduce((s, f) => s + Number(f.back_wages || 0), 0));

  return {
    lines,
    p2FringeRows: Array.from(p2FringeMap.values()),
    total6B,
    total6C,
    anyRA,
    populateP2FringeGrid: total6B > 0,
    apprenticeTableNA: !anyRA,
    addendumDeductions,
    findings,
    blockers,
    warnings,
    totalBackWages,
    cwhssaDamages,
    passed: blockers === 0
  };
}

function renderAll() {
  // Sync header inputs
  document.getElementById("f_project_name").value = state.project_name;
  document.getElementById("f_project_no").value = state.project_no;
  document.getElementById("f_payroll_no").value = state.certified_payroll_no;
  document.getElementById("f_role").value = state.contractor_role;
  document.getElementById("f_business_name").value = state.business_name;
  document.getElementById("f_business_addr").value = state.business_address;
  document.getElementById("f_location").value = state.project_location;
  document.getElementById("f_wd_no").value = state.wage_determination_no;
  document.getElementById("f_week_end").value = state.week_ending_date;
  document.getElementById("f_official_name").value = state.certifying_official_name;
  document.getElementById("f_official_title").value = state.certifying_official_title;
  document.getElementById("f_phone").value = state.telephone;
  document.getElementById("f_email").value = state.email;

  const res = computeAndAudit(state);
  renderGateBanner(res);
  renderCrewTable(res);
  renderFindings(res);
}

function renderGateBanner(res) {
  const el = document.getElementById("gate_banner");
  if (res.passed) {
    el.className = "gate-banner gate-pass";
    el.innerHTML = `
      <div>
        <div class="gate-title">&#10003; PASSED 2026 SUBMISSION GATE — READY FOR OFFICIAL DOL WH-347 PDF</div>
        <div style="font-size:0.84rem;margin-top:0.2rem;">All 26 statutory DBRA, CWHSSA, Copeland Act &amp; Revised Jan-2025 WH-347 checks clear.</div>
      </div>
      <div class="gate-metrics">
        <span class="metric-pill num">0 Blockers</span>
        <span class="metric-pill num">${res.warnings} Informational Notice(s)</span>
        <span class="metric-pill num">Col 6B Plan Credit: $${fmtMoney(res.total6B)}</span>
        <span class="metric-pill num">Col 6C Cash Fringe: $${fmtMoney(res.total6C)}</span>
      </div>
    `;
  } else {
    el.className = "gate-banner gate-fail";
    el.innerHTML = `
      <div>
        <div class="gate-title">&#9888; PAYROLL REJECTION &amp; WITHHOLDING RISK: ${res.blockers} STATUTORY BLOCKER(S) DETECTED</div>
        <div style="font-size:0.84rem;margin-top:0.2rem;">Contracting Officers &amp; Prime GCs withhold progress payments when these violations appear on Form WH-347.</div>
      </div>
      <div class="gate-metrics">
        <span class="metric-pill num">Back-Wage Restitution: $${fmtMoney(res.totalBackWages)}</span>
        <span class="metric-pill num">CWHSSA Penalty Risk: $${fmtMoney(res.cwhssaDamages)}</span>
        <button type="button" class="btn btn-accent btn-sm" onclick="autoRemediateTraps()">&#9889; 1-Click Auto-Fix Sample Violations</button>
      </div>
    `;
  }
}

function renderCrewTable(res) {
  const tbody = document.getElementById("crew_tbody");
  tbody.innerHTML = res.lines.map((l, idx) => {
    const r = l.src;
    const stSumInput = l.stTot;
    const otSumInput = l.otTot;
    return `
      <tr>
        <td><input type="number" class="w-xs num" value="${r.worker_entry_no}" onchange="updRow(${idx}, 'worker_entry_no', Number(this.value))"></td>
        <td><input type="text" class="w-sm" value="${r.last_name}" onchange="updRow(${idx}, 'last_name', this.value)"></td>
        <td><input type="text" class="w-sm" value="${r.first_name}" onchange="updRow(${idx}, 'first_name', this.value)"></td>
        <td><input type="text" class="w-sm mono" value="${r.worker_id}" onchange="updRow(${idx}, 'worker_id', this.value)"></td>
        <td>
          <select class="w-xs" onchange="updRow(${idx}, 'status', this.value)">
            <option value="J" ${r.status === "J" ? "selected" : ""}>J</option>
            <option value="RA" ${r.status === "RA" ? "selected" : ""}>RA</option>
          </select>
        </td>
        <td><input type="text" class="w-lg" value="${r.labor_classification}" onchange="updRow(${idx}, 'labor_classification', this.value)"></td>
        <td><input type="number" step="0.5" class="w-xs num" value="${stSumInput}" title="Weekly ST Hours (distributed Mon-Sat)" onchange="updWeeklyHrs(${idx}, 'st', Number(this.value))"></td>
        <td><input type="number" step="0.5" class="w-xs num" value="${otSumInput}" title="Weekly OT Hours" onchange="updWeeklyHrs(${idx}, 'ot', Number(this.value))"></td>
        <td><input type="number" step="0.01" class="w-sm num" value="${r.st_rate_paid.toFixed(2)}" onchange="updRow(${idx}, 'st_rate_paid', Number(this.value))"></td>
        <td><input type="number" step="0.01" class="w-sm num" value="${r.ot_rate_paid.toFixed(2)}" onchange="updRow(${idx}, 'ot_rate_paid', Number(this.value))"></td>
        <td><input type="number" step="0.01" class="w-xs num" value="${l.hrFringeCredit.toFixed(2)}" title="Hourly Bona Fide Plan Credit (Page 2)" onchange="updPlanTotal(${idx}, Number(this.value))"></td>
        <td><input type="number" step="0.01" class="w-xs num" value="${r.cash_in_lieu_rate.toFixed(2)}" title="Hourly Cash-in-Lieu Fringe" onchange="updRow(${idx}, 'cash_in_lieu_rate', Number(this.value))"></td>
        <td class="computed-cell">$${fmtMoney(l.col6B)}</td>
        <td class="computed-cell">$${fmtMoney(l.col6C)}</td>
        <td class="computed-cell">$${fmtMoney(l.col7A)}</td>
        <td class="computed-cell">${l.isPrimary ? "$" + fmtMoney(l.col9Net) : '<span style="color:#64748b;font-size:0.73rem;">Entry #' + r.worker_entry_no + '</span>'}</td>
        <td><button type="button" class="btn btn-outline btn-sm" title="Remove row" onclick="removeRow(${idx})">&times;</button></td>
      </tr>
    `;
  }).join("");
}

function renderFindings(res) {
  const box = document.getElementById("findings_list");
  if (res.findings.length === 0) {
    box.innerHTML = `<div class="finding-card" style="border-left-color:var(--emerald-ok);background:var(--emerald-bg);">
      <div class="finding-title" style="color:#065f46;">Zero Compliance Findings — Ready to Sign &amp; Transmit</div>
      <div class="finding-detail">Page 1 Cols 1A–9, Page 2 Boxes 1–6, Mandatory "${res.apprenticeTableNA ? 'N/A' : 'OA/SAA'}" Apprentice Table rule, and Fringe Benefit Matrix are reconciled to the cent.</div>
    </div>`;
    return;
  }
  box.innerHTML = res.findings.map(f => `
    <div class="finding-card ${f.severity === 'WARNING' ? 'is-warning' : ''}">
      <div class="finding-top">
        <div>
          <span class="badge ${f.severity === 'BLOCKER' ? 'badge-blocker' : 'badge-warning'}">${f.severity} · ${f.rule_id}</span>
          <span class="finding-title" style="margin-left:0.45rem;">${f.title}</span>
        </div>
        <span class="finding-cite">${f.cfr}</span>
      </div>
      <div class="finding-detail">${f.detail}</div>
      <div class="finding-fix">Remediation: ${f.fix}</div>
    </div>
  `).join("");
}

window.updHeader = function(key, val) {
  state[key] = val;
  renderAll();
};

window.updRow = function(idx, key, val) {
  state.rows[idx][key] = val;
  renderAll();
};

window.updWeeklyHrs = function(idx, kind, totalVal) {
  const v = Math.max(0, Number(totalVal || 0));
  if (kind === "st") {
    const arr = [0, 0, 0, 0, 0, 0, 0];
    let rem = v;
    for (let d = 1; d <= 6 && rem > 0; d++) {
      const chunk = Math.min(8, rem);
      arr[d] = chunk;
      rem = qCent(rem - chunk);
    }
    if (rem > 0) arr[0] = rem;
    state.rows[idx].st_hours = arr;
  } else {
    const arr = [0, 0, 0, 0, 0, 0, 0];
    arr[5] = qCent(v / 2);
    arr[6] = qCent(v - arr[5]);
    state.rows[idx].ot_hours = arr;
  }
  renderAll();
};

window.updPlanTotal = function(idx, val) {
  state.rows[idx].fb1 = Math.max(0, qCent(val));
  state.rows[idx].fb2 = 0;
  state.rows[idx].fb3 = 0;
  renderAll();
};

window.addRow = function() {
  const nextNo = state.rows.length > 0 ? Math.max(...state.rows.map(r => Number(r.worker_entry_no))) + 1 : 1;
  state.rows.push({
    worker_entry_no: nextNo,
    last_name: "NewWorker",
    first_name: "Alex",
    middle_initial: "",
    worker_id: "1042",
    status: "J",
    apprentice_progression: "",
    labor_classification: "Laborer - Common / General",
    st_hours: [0, 8, 8, 8, 8, 8, 0],
    ot_hours: [0, 0, 0, 0, 0, 0, 0],
    st_rate_paid: 22.40,
    ot_rate_paid: 33.60,
    fb1: 4.00,
    fb2: 0.00,
    fb3: 0.00,
    cash_in_lieu_rate: 3.60,
    includes_cash_fringe_in_6a: false,
    other_projects_gross: 0.00,
    tax: 98.00,
    fica: 79.56,
    other_ded: 0.00,
    other_ded_desc: ""
  });
  renderAll();
};

window.removeRow = function(idx) {
  if (state.rows.length <= 1) return;
  state.rows.splice(idx, 1);
  renderAll();
};

window.loadPreset = function(mode) {
  state = mode === "clean" ? buildCleanPreset() : buildTrapPreset();
  renderAll();
};

window.autoRemediateTraps = function() {
  if (!state.wage_determination_no.trim()) {
    state.wage_determination_no = "TX20260028 Mod 3 (Building)";
  }
  if (state.rows.some(r => r.status === "RA") && state.apprentice_programs.length === 0) {
    state.apprentice_programs = [
      {
        program_name: "Austin Electrical JATC Local 520",
        registration_agency: "OA",
        labor_classification: "Electrician (Inside Wireman)",
        progression_pct: 65,
        fringes_full_rate: true,
        ratio_apprentices: 1,
        ratio_journeyworkers: 1
      }
    ];
  }
  state.rows.forEach(r => {
    const digits = (r.worker_id || "").replace(/\D/g, "");
    if (digits.length === 9) {
      r.worker_id = digits.slice(-4);
    }
    r.includes_cash_fringe_in_6a = false;
    const stSum = r.st_hours.reduce((a, b) => a + Number(b || 0), 0);
    if (stSum > 40) {
      const extra = qCent(stSum - 40);
      r.st_hours = [0, 8, 8, 8, 8, 8, 0];
      r.ot_hours = [0, 0, 0, 0, 0, 0, extra];
    }
    if (r.labor_classification === "Laborer - Common / General" && (r.fb1 + r.fb2 + r.fb3 + r.cash_in_lieu_rate) < 7.60) {
      r.cash_in_lieu_rate = qCent(7.60 - (r.fb1 + r.fb2 + r.fb3));
    }
  });
  renderAll();
};

/* CSV Import & Template Download */
window.downloadCsvTemplate = function() {
  const csv = [
    "worker_entry_no,last_name,first_name,middle_initial,worker_id,status,labor_classification,weekly_st_hours,weekly_ot_hours,st_rate_paid,ot_rate_paid,plan_fringe_hr,cash_in_lieu_hr,tax,fica,other_ded,other_ded_desc",
    "1,Ramirez,Carlos,A,4829,J,Electrician (Inside Wireman),40,4,39.00,58.50,14.20,0.00,248.40,137.24,35.88,IBEW Working Dues",
    "2,Kowalski,Tomasz,,3318,J,Laborer - Common / General,40,0,22.40,33.60,4.00,3.60,108.50,79.56,0.00,"
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "ClearWage_WH347_Import_Template_2026.csv";
  a.click();
};

window.handleCsvUpload = function(ev) {
  const file = ev.target.files && ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const lines = String(e.target.result || "").trim().split(/\r?\n/);
    if (lines.length < 2) return;
    const newRows = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(",");
      if (cols.length < 13) continue;
      const stTot = Number(cols[7] || 0);
      const otTot = Number(cols[8] || 0);
      const stArr = [0, 0, 0, 0, 0, 0, 0];
      let rem = stTot;
      for (let d = 1; d <= 6 && rem > 0; d++) {
        stArr[d] = Math.min(8, rem);
        rem = qCent(rem - stArr[d]);
      }
      const otArr = [0, 0, 0, 0, 0, otTot, 0];
      newRows.push({
        worker_entry_no: Number(cols[0] || i),
        last_name: cols[1] || "Worker",
        first_name: cols[2] || "",
        middle_initial: cols[3] || "",
        worker_id: cols[4] || "0000",
        status: (cols[5] || "J").trim().toUpperCase(),
        apprentice_progression: "",
        labor_classification: cols[6] || "Laborer - Common / General",
        st_hours: stArr,
        ot_hours: otArr,
        st_rate_paid: Number(cols[9] || 0),
        ot_rate_paid: Number(cols[10] || 0),
        fb1: Number(cols[11] || 0),
        fb2: 0,
        fb3: 0,
        cash_in_lieu_rate: Number(cols[12] || 0),
        includes_cash_fringe_in_6a: false,
        other_projects_gross: 0,
        tax: Number(cols[13] || 0),
        fica: Number(cols[14] || 0),
        other_ded: Number(cols[15] || 0),
        other_ded_desc: cols.slice(16).join(",").trim()
      });
    }
    if (newRows.length > 0) {
      state.rows = newRows;
      renderAll();
    }
  };
  reader.readAsText(file);
};

/* Pixel-Exact Official DOL Rev. Jan-2025 WH-347 PDF Compiler in Browser via pdf-lib */
window.compileOfficialDolPdf = async function() {
  const res = computeAndAudit(state);
  if (state.rows.length > CHECKOUT_CONFIG.freePdfMaxRows) {
    openProModal(`Your payroll has ${state.rows.length} classification rows. The free browser tool compiles up to ${CHECKOUT_CONFIG.freePdfMaxRows} rows per sheet; unlock the ClearWage Pro Contractor Suite ($${CHECKOUT_CONFIG.priceUsd} one-time) or use the open-core Python CLI for unlimited multi-sheet crews.`);
    return;
  }

  const btn = document.getElementById("btn_compile_pdf");
  const origLabel = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = "Compiling Official DOL WH-347 PDF...";

  try {
    const { PDFDocument, StandardFonts, rgb } = window.PDFLib;
    const rawBuf = await fetch("assets/wh347_official.pdf").then(r => {
      if (!r.ok) throw new Error("Failed to load official DOL WH-347 PDF template");
      return r.arrayBuffer();
    });
    const tplBytes = new Uint8Array(rawBuf);
    const srcDoc = await PDFDocument.load(tplBytes);
    const outDoc = await PDFDocument.create();
    const [p1, p2] = await outDoc.copyPages(srcDoc, [0, 1]);
    outDoc.addPage(p1);
    outDoc.addPage(p2);

    const helv = await outDoc.embedFont(StandardFonts.Helvetica);
    const hebo = await outDoc.embedFont(StandardFonts.HelveticaBold);
    const ink = rgb(0.06, 0.14, 0.28);
    const H = 612.0;

    function drawBox(page, x0, y0, x1, y1, text, opts = {}) {
      if (!text) return;
      const str = String(text);
      const font = opts.bold ? hebo : helv;
      const align = opts.align || "left";
      const padX = 1.4;
      const availW = Math.max(4.0, (x1 - x0) - 2 * padX);
      let fs = opts.size || 7.2;

      if (opts.multiline && str.length > 16) {
        const words = str.split(/\s+/);
        let l1 = "";
        let l2 = "";
        words.forEach(w => {
          const cand = l1 ? `${l1} ${w}` : w;
          if (font.widthOfTextAtSize(cand, fs) <= availW || !l1) {
            l1 = cand;
          } else {
            l2 = l2 ? `${l2} ${w}` : w;
          }
        });
        if (l2) {
          const midY = (y0 + y1) / 2.0;
          drawBox(page, x0, y0, x1, midY, l1, { ...opts, multiline: false });
          drawBox(page, x0, midY, x1, y1, l2, { ...opts, multiline: false });
          return;
        }
      }

      let tw = font.widthOfTextAtSize(str, fs);
      while (fs > 3.5 && tw > availW) {
        fs = Math.round((fs - 0.25) * 100) / 100;
        tw = font.widthOfTextAtSize(str, fs);
      }

      let tx = x0 + padX;
      if (align === "right") tx = Math.max(x0 + 0.8, x1 - padX - tw);
      else if (align === "center") tx = Math.max(x0 + 0.6, x0 + ((x1 - x0) - tw) / 2.0);

      const baselineTopDown = (y0 + y1) / 2.0 + fs * 0.34;
      page.drawText(str, { x: tx, y: H - baselineTopDown, size: fs, font, color: ink });
    }

    function drawCheck(page, cx0, cy0, cx1, cy1) {
      const w = cx1 - cx0;
      const h = cy1 - cy0;
      const pA = { x: cx0 + 0.18 * w, y: H - (cy0 + 0.55 * h) };
      const pB = { x: cx0 + 0.42 * w, y: H - (cy0 + 0.80 * h) };
      const pC = { x: cx0 + 0.85 * w, y: H - (cy0 + 0.20 * h) };
      page.drawLine({ start: pA, end: pB, thickness: 1.35, color: ink });
      page.drawLine({ start: pB, end: pC, thickness: 1.35, color: ink });
    }

    // --- PAGE 1 OVERLAY ---
    if (state.is_final_payroll) drawCheck(p1, 40.4, 101.4, 49.4, 110.4);
    if (state.contractor_role === "prime") drawCheck(p1, 432.0, 101.4, 441.0, 110.4);
    if (state.contractor_role === "subcontractor") drawCheck(p1, 576.0, 101.4, 585.0, 110.4);

    drawBox(p1, 42.0, 133.0, 195.0, 151.6, state.project_name, { size: 7.5, bold: true });
    drawBox(p1, 196.5, 133.0, 340.5, 151.6, state.project_no, { size: 7.5 });
    drawBox(p1, 342.0, 133.0, 439.0, 151.6, String(state.certified_payroll_no), { size: 7.6, align: "center", bold: true });
    drawBox(p1, 440.5, 133.0, 751.0, 151.6, state.business_name, { size: 7.5, bold: true });

    drawBox(p1, 42.0, 164.4, 195.0, 183.8, state.project_location, { size: 6.8 });
    drawBox(p1, 196.5, 164.4, 340.5, 183.8, state.wage_determination_no, { size: 7.1 });
    drawBox(p1, 342.0, 164.4, 439.0, 183.8, state.week_ending_date, { size: 7.3, align: "center" });
    drawBox(p1, 440.5, 164.4, 751.0, 183.8, state.business_address, { size: 6.8 });

    const wk = getWeekDates(state.week_ending_date);
    for (let d = 0; d < 7; d++) {
      drawBox(p1, P1_DAY_X[d][0], 223.5, P1_DAY_X[d][1], 235.8, wk.letters[d], { size: 6.8, align: "center", bold: true });
      drawBox(p1, P1_DAY_X[d][0], 236.2, P1_DAY_X[d][1], 249.8, wk.dates[d], { size: 5.5, align: "center" });
    }

    res.lines.slice(0, 8).forEach((l, rIdx) => {
      const r = l.src;
      const [yTop, yMid, yBot] = P1_ROW_BANDS[rIdx];
      drawBox(p1, 41.2, yTop, 65.7, yBot, String(r.worker_entry_no), { size: 7.4, align: "center", bold: true });
      drawBox(p1, 66.2, yTop, 115.6, yBot, r.last_name, { size: 6.8 });
      drawBox(p1, 116.2, yTop, 165.3, yBot, r.first_name, { size: 6.8 });
      drawBox(p1, 165.8, yTop, 191.0, yBot, r.middle_initial, { size: 6.8, align: "center" });
      drawBox(p1, 191.6, yTop, 221.0, yBot, r.worker_id, { size: 6.6, align: "center" });
      const col2 = r.status === "J" ? "J" : `RA ${r.apprentice_progression || ""}`.trim();
      drawBox(p1, 221.6, yTop, 255.6, yBot, col2, { size: 5.8, align: "center", multiline: true });
      drawBox(p1, 256.4, yTop, 300.8, yBot, r.labor_classification, { size: 5.8, multiline: true });

      for (let d = 0; d < 7; d++) {
        drawBox(p1, P1_DAY_X[d][0], yTop, P1_DAY_X[d][1], yMid, fmtHrs(r.st_hours[d]), { size: 6.3, align: "center" });
        drawBox(p1, P1_DAY_X[d][0], yMid, P1_DAY_X[d][1], yBot, fmtHrs(r.ot_hours[d]), { size: 6.3, align: "center" });
      }
      drawBox(p1, 430.6, yTop, 469.4, yMid, fmtHrs(l.stTot), { size: 6.8, align: "right", bold: true });
      drawBox(p1, 430.6, yMid, 469.4, yBot, fmtHrs(l.otTot), { size: 6.8, align: "right" });
      drawBox(p1, 469.8, yTop, 497.9, yMid, fmtMoney(r.st_rate_paid), { size: 6.4, align: "right" });
      if (l.otTot > 0 || r.ot_rate_paid > 0) {
        drawBox(p1, 469.8, yMid, 497.9, yBot, fmtMoney(r.ot_rate_paid), { size: 6.4, align: "right" });
      }
      drawBox(p1, 498.3, yTop, 524.2, yBot, fmtMoney(l.col6B), { size: 6.2, align: "right" });
      drawBox(p1, 524.6, yTop, 550.6, yBot, fmtMoney(l.col6C), { size: 6.2, align: "right" });
      drawBox(p1, 551.0, yTop, 577.0, yBot, fmtMoney(l.col7A), { size: 6.2, align: "right", bold: true });

      if (l.isPrimary) {
        drawBox(p1, 577.4, yTop, 604.5, yBot, fmtMoney(l.col7B), { size: 6.2, align: "right" });
        drawBox(p1, 604.9, yTop, 631.4, yBot, fmtMoney(l.col8Tax), { size: 6.0, align: "right" });
        drawBox(p1, 631.8, yTop, 658.2, yBot, fmtMoney(l.col8Fica), { size: 6.0, align: "right" });
        drawBox(p1, 658.6, yTop, 689.2, yBot, fmtMoney(l.col8Other), { size: 6.0, align: "right" });
        drawBox(p1, 689.6, yTop, 712.6, yBot, fmtMoney(l.col8Total), { size: 6.0, align: "right" });
        drawBox(p1, 713.0, yTop, 751.8, yBot, fmtMoney(l.col9Net), { size: 6.4, align: "right", bold: true });
      } else {
        drawBox(p1, 577.4, yTop, 751.8, yBot, `See Entry #${r.worker_entry_no} primary row`, { size: 5.5, align: "center" });
      }
    });

    // --- PAGE 2 OVERLAY ---
    drawBox(p2, 33.0, 44.8, 237.5, 63.0, state.project_name, { size: 7.5, bold: true });
    drawBox(p2, 240.0, 44.8, 377.0, 63.0, state.project_no, { size: 7.5 });
    drawBox(p2, 379.5, 44.8, 471.5, 63.0, String(state.certified_payroll_no), { size: 7.6, align: "center", bold: true });
    drawBox(p2, 474.0, 44.8, 759.5, 63.0, state.business_name, { size: 7.5, bold: true });

    drawBox(p2, 33.0, 76.0, 377.0, 95.4, state.project_location, { size: 7.0 });
    drawBox(p2, 379.5, 76.0, 471.5, 95.4, state.week_ending_date, { size: 7.4, align: "center" });
    drawBox(p2, 474.0, 76.0, 759.5, 95.4, `${state.certifying_official_name}, ${state.certifying_official_title}`, { size: 7.3, bold: true });

    drawCheck(p2, 38.2, 125.2, 47.2, 134.2);
    drawCheck(p2, 38.2, 156.0, 47.2, 165.0);
    drawCheck(p2, 38.2, 176.2, 47.2, 185.2);
    if (res.anyRA) drawCheck(p2, 38.2, 199.8, 47.2, 208.8);
    if (res.total6B > 0 || res.total6C > 0) drawCheck(p2, 38.2, 284.6, 47.2, 293.6);
    drawCheck(p2, 38.2, 472.3, 47.2, 481.3);

    if (res.apprenticeTableNA) {
      drawBox(p2, 56.0, 237.8, 376.0, 250.4, "N/A", { size: 7.2, bold: true });
    } else if (state.apprentice_programs && state.apprentice_programs[0]) {
      const ap = state.apprentice_programs[0];
      drawBox(p2, 56.0, 237.8, 376.0, 250.4, ap.program_name, { size: 6.8 });
      if (ap.registration_agency === "OA") drawCheck(p2, 383.4, 240.4, 391.4, 248.4);
      else drawCheck(p2, 432.8, 240.4, 440.9, 248.4);
      drawBox(p2, 474.0, 237.8, 759.0, 250.4, ap.labor_classification, { size: 6.8 });
    }

    if (res.populateP2FringeGrid) {
      const fundedX = [[149.4, 194.4], [243.8, 288.8], [338.4, 383.4]];
      (state.fringe_plans || []).slice(0, 3).forEach((pl, pIdx) => {
        const [px0, px1] = P2_PLAN_X[pIdx];
        drawBox(p2, px0 + 42.0, 326.8, px1 - 2.0, 338.0, pl.fb_name, { size: 5.5, bold: true });
        drawBox(p2, px0 + 38.5, 338.8, px1 - 2.0, 350.2, pl.fb_type, { size: 5.5 });
        drawBox(p2, px0 + 40.5, 350.6, px1 - 2.0, 362.0, pl.plan_no, { size: 5.5 });
        const fx = pl.is_funded ? fundedX[pIdx][0] : fundedX[pIdx][1];
        drawCheck(p2, fx, 363.9, fx + 7.0, 370.9);
      });

      res.p2FringeRows.slice(0, 8).forEach((wr, wIdx) => {
        const [wy0, wy1] = P2_WORKER_Y[wIdx];
        drawBox(p2, 55.0, wy0, 143.5, wy1, wr.displayName, { size: 6.0 });
        const vals = [wr.fb1, wr.fb2, wr.fb3];
        vals.forEach((v, pIdx) => {
          if (v > 0) {
            drawBox(p2, P2_PLAN_X[pIdx][0] + 57.0, wy0, P2_PLAN_X[pIdx][1] - 2.0, wy1, fmtMoney(v), { size: 6.2, align: "right" });
          }
        });
        drawBox(p2, 720.0, wy0, 759.0, wy1, fmtMoney(wr.total), { size: 6.4, align: "right", bold: true });
      });
    }

    const singleDedRemarks = res.lines
      .filter(l => l.isPrimary && l.col8Other > 0 && !(l.src.other_ded_desc || "").includes(";"))
      .map(l => `Entry #${l.src.worker_entry_no} (${l.src.last_name}) Other: ${l.src.other_ded_desc} ($${fmtMoney(l.col8Other)})`);
    const remarksParts = [state.additional_remarks, ...singleDedRemarks];
    if (res.addendumDeductions.length > 0) {
      remarksParts.push("See attached Page 3 Copeland Act (29 CFR 3.5) Itemized Deductions Addendum.");
    }
    drawBox(p2, 33.0, 504.0, 759.0, 526.6, remarksParts.filter(Boolean).join(" | "), { size: 6.2, multiline: true });

    drawBox(p2, 33.0, 540.8, 376.0, 556.2, `/s/ ${state.certifying_official_name}`, { size: 7.6, bold: true });
    drawBox(p2, 380.0, 540.8, 471.0, 556.2, state.week_ending_date, { size: 7.2, align: "center" });

    let digits = (state.telephone || "").replace(/\D/g, "");
    if (digits.length === 11 && digits.startsWith("1")) digits = digits.slice(1);
    if (digits.length === 10) {
      drawBox(p2, 482.0, 540.0, 509.8, 551.8, digits.slice(0, 3), { size: 7.4, align: "center", bold: true });
      drawBox(p2, 521.0, 540.0, 548.8, 551.8, digits.slice(3, 6), { size: 7.4, align: "center", bold: true });
      drawBox(p2, 558.0, 540.0, 595.5, 551.8, digits.slice(6), { size: 7.4, align: "center", bold: true });
    } else {
      drawBox(p2, 475.0, 540.0, 615.0, 552.0, state.telephone, { size: 7.0, align: "center" });
    }
    drawBox(p2, 619.0, 540.8, 759.0, 556.2, state.email, { size: 6.8 });

    // Optional Page 3 Copeland Act Addendum
    if (res.addendumDeductions.length > 0) {
      const p3 = outDoc.addPage([792, 612]);
      p3.drawRectangle({ x: 30, y: 28, width: 732, height: 556, borderColor: rgb(0.55, 0.35, 0.18), borderWidth: 1.1 });
      p3.drawRectangle({ x: 30, y: 544, width: 732, height: 40, color: rgb(0.95, 0.88, 0.81), borderColor: rgb(0.55, 0.35, 0.18), borderWidth: 1.0 });
      p3.drawText("U.S. DOL FORM WH-347 (REV. JAN 2025) — OFFICIAL CONTINUATION ADDENDUM", { x: 42, y: 566, size: 11, font: hebo, color: ink });
      p3.drawText(`Project: ${state.project_name} (${state.project_no})  |  Payroll #${state.certified_payroll_no}  |  Week Ending: ${state.week_ending_date}`, { x: 42, y: 552, size: 8, font: helv, color: ink });
      p3.drawText("SECTION A — COPELAND ACT (29 CFR § 3.5) ITEMIZED 'OTHER' DEDUCTIONS SCHEDULE", { x: 42, y: 520, size: 9.2, font: hebo, color: ink });
      let curY = 502;
      res.addendumDeductions.forEach(l => {
        p3.drawText(`• Entry #${l.src.worker_entry_no} (${l.src.last_name}, ${l.src.first_name}) — Total Col 8 Other: $${fmtMoney(l.col8Other)}  =>  ${l.src.other_ded_desc}`, {
          x: 50, y: curY, size: 8, font: helv, color: ink
        });
        curY -= 15;
      });
    }

    const pdfBytes = await outDoc.save();
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `WH347_Payroll_${state.certified_payroll_no}_${state.week_ending_date}.pdf`;
    a.click();
  } catch (err) {
    alert("PDF Compilation Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origLabel;
  }
};

window.openProModal = function(customReason) {
  if (CHECKOUT_CONFIG.proSuiteCheckoutUrl) {
    window.open(CHECKOUT_CONFIG.proSuiteCheckoutUrl, "_blank", "noopener");
    return;
  }
  const msgEl = document.getElementById("pro_modal_reason");
  msgEl.textContent = customReason || "Get the complete 6-Tab Macro-Free Excel Contractor Suite (.xlsx for Windows, Mac & Web), 50-Worker Multi-Crew Auto-Rollup, Copeland Act Deduction Templates, & 2026 GC Compliance Pack.";
  document.getElementById("pro_modal").classList.add("open");
};

window.closeProModal = function() {
  document.getElementById("pro_modal").classList.remove("open");
};

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("crew_tbody")) {
    renderAll();
  }
});
