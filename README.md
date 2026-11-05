# ClearWage WH-347 (`OMB 1235-0008` · Mandatory Oct 1, 2026)

**Deterministic U.S. DOL Revised Form WH-347 Certified Payroll Compliance Auditor, DBRA/CWHSSA Overtime Calculator & Pixel-Aligned Official PDF Compiler (Browser + CLI + MCP Server).**

[![Live Browser Validator & PDF Compiler](https://img.shields.io/badge/Live_Web_App-100%25_Client--Side_(Zero_PII_Upload)-0c2340?style=for-the-badge)](https://zchryst.github.io/clearwage-wh347/)
[![License: MIT](https://img.shields.io/badge/License-MIT-047857?style=for-the-badge)](LICENSE)
[![OMB Control No.](https://img.shields.io/badge/OMB_1235--0008-Exp._01%2F31%2F2028-b45309?style=for-the-badge)](https://zchryst.github.io/clearwage-wh347/wh-347-2026-changes.html)

---

## Why ClearWage WH-347 Exists

On **September 30, 2026**, legacy pre-2025 Form WH-347 templates officially expired. Beginning **October 1, 2026**, federal Contracting Officers, municipal sponsors, and prime contractors mandate the **Revised January 2025 Form WH-347 (`OMB Control No. 1235-0008`, Exp. `01/31/2028`)**.

Two acute pain points hit subcontractors, bookkeepers, and AI accounting agents immediately:

1. **The official DOL `wh347.pdf` has zero interactive AcroForm fields** — it is a flat `792 × 612` pt vector graphic.
2. **Nine new statutory traps trigger progress-payment holdbacks**, including the mandatory **SAM.gov Wage Determination No.** header, strict separation of **Col 6A** (base cash rate excluding cash fringes), **Col 6B** (weekly bona fide plan credit `$`), and **Col 6C** (weekly cash-in-lieu `$`), **Split-Classification Col 1A Entry No. deduplication** of Cols 7B/8/9, **Page 2 Box 4 `"N/A"` rule**, and **Page 2 `6-Plan × 8-Worker` Hourly Credit Matrix**.

---

## Live Browser App (100% Local — Zero Payroll Data Leaves Your Device)

👉 **Launch Free Validator & Official DOL PDF Compiler:** **https://zchryst.github.io/clearwage-wh347/**

- **26-Rule Deterministic Statutory Audit** (`WH347-001` through `WH347-026`) with `29 CFR Parts 3 & 5` and `40 U.S.C. § 3702 (CWHSSA)` citations, exact back-wage restitution math, and `$32/day` CWHSSA liquidated damages alerts.
- **Pixel-Exact Official DOL PDF Generation** in-browser (`pdf-lib`) or via Python (`pymupdf`), including automatic **Page 3 Copeland Act (`29 CFR § 3.5`) Itemized Deductions & Continuation Addenda**.
- **Free 5-Worker Macro-Free Starter `.xlsx`** & **[50-Worker Pro Contractor Excel Suite ($79)](https://www.etsy.com/listing/4610186233/2026-certified-payroll-excel-template)** (runs on Windows Excel, Mac Excel, Excel Web & Google Sheets with zero blocked `.xlsm` VBA macros).

---

## Python CLI Quickstart

```bash
pip install git+https://github.com/zchryst/clearwage-wh347.git

# 1. Run the 26-rule statutory audit on the built-in 6-trap rejection sample:
clearwage audit demo-traps

# 2. Audit a clean multi-classification + registered apprentice payroll:
clearwage audit demo-clean

# 3. Compile a pixel-aligned 3-page Official DOL WH-347 PDF packet:
clearwage render-pdf demo-clean -o WH347_Signed_Packet.pdf

# 4. Audit & compile your own JSON payroll export:
clearwage audit my_payroll_week4.json
clearwage render-pdf my_payroll_week4.json -o WH347_Week4.pdf
```

---

## Model Context Protocol (MCP) Server for Claude, Cursor & Bookkeeping Agents

LLMs hallucinate Davis-Bacon half-time overtime premiums (`29 CFR § 5.32`) and cannot natively overlay flat government PDFs. Connect `clearwage-mcp` to give any MCP-compatible agent cent-exact certified payroll tools:

### Tools Exposed
| Tool Name | Description |
| :--- | :--- |
| `calculate_dbra_overtime` | Exact `29 CFR § 5.32` / `CWHSSA` / `FLSA` overtime floor (`1.5× max(WD basic, actual base) + 1.0× prevailing fringe`) without 1.5× cash-fringe overpayment. |
| `audit_wh347_payroll` | Runs all 26 deterministic compliance checks (`WH347-001`..`WH347-026`) on a Revised Jan-2025 WH-347 submission and computes exact back-wage & CWHSSA penalty exposure. |
| `generate_wh347_official_pdf` | Audits and compiles a pixel-aligned Revised Jan-2025 Form WH-347 PDF (with multi-page continuation & Copeland Act addenda) onto the official DOL vector layout. |

### `claude_desktop_config.json` / `.cursor/mcp.json`
```json
{
  "mcpServers": {
    "clearwage-wh347": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/zchryst/clearwage-wh347.git",
        "clearwage-mcp"
      ]
    }
  }
}
```

---

## Statutory Rule Coverage (`WH347-001` – `WH347-026`)

- **`WH347-001` – `WH347-006`**: Prime/Subcontractor role, sequential payroll numbering, mandatory SAM.gov Wage Determination No., County/State location, Certifying Official Name/Title, and new Page 2 Phone/Email blocks.
- **`WH347-007` – `WH347-010`**: `29 CFR § 5.5(a)(3)(ii)` 9-digit SSN privacy blocker, split-classification shared `Col 1A` Worker Entry No. invariant, and single-row Col 7B/8/9 rollup.
- **`WH347-011` – `WH347-013` & `WH347-020`**: Journeyworker (`J`) vs. Registered Apprentice (`RA`) progression validation, OA/SAA Page 2 Box 4 registration verification, mandatory `"N/A"` rule when 0 apprentices worked, and on-site `RA:J` ratio enforcement.
- **`WH347-014` – `WH347-019`**: Col 6A cash-fringe contamination blocker, SF-1444 unlisted classification check, prevailing ST + fringe shortfall restitution, `29 CFR § 5.32` DBRA/FLSA overtime floor, and CWHSSA `>40` weekly hour cross-classification check (`$32/day` liquidated damages).
- **`WH347-021` – `WH347-026`**: Unfunded plan prior written DOL approval (`29 CFR § 5.28`), Col 7B vs. Col 7A reconciliation, Copeland Anti-Kickback Act (`29 CFR §§ 3.5–3.6`) deduction itemization, Col 9 Net Pay tie-out, and automatic Addendum generation.

---

## Disclaimer

ClearWage WH-347 provides deterministic calculation and document-compilation software implementing published U.S. Department of Labor Wage and Hour Division instructions (`OMB Control No. 1235-0008`, `29 CFR Parts 3 & 5`, `40 U.S.C. §§ 3141–3148`, `40 U.S.C. §§ 3701–3708`). It does not constitute legal advice and is not affiliated with or endorsed by the U.S. Department of Labor.
