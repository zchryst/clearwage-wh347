"""CLI entry point for ClearWage WH-347 (audit, PDF compiler, Excel builder)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from clearwage_wh347.auditor import audit_payroll
from clearwage_wh347.excel_generator import build_free_starter_workbook, build_pro_contractor_workbook
from clearwage_wh347.models import PayrollSubmission
from clearwage_wh347.pdf_renderer import render_wh347_pdf
from clearwage_wh347.samples import build_buggy_payroll_trap_sample, build_clean_hvac_subcontractor_sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clearwage",
        description="Deterministic 2026 Revised DOL Form WH-347 (OMB 1235-0008) Compliance Engine",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_aud = sub.add_parser("audit", help="Audit a WH-347 payroll JSON file against 26 DBRA/CWHSSA rules")
    p_aud.add_argument("input_json", help="Path to payroll JSON payload (or 'demo-clean' / 'demo-traps')")
    p_aud.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    p_pdf = sub.add_parser("render-pdf", help="Compile pixel-aligned official DOL Form WH-347 PDF")
    p_pdf.add_argument("input_json", help="Path to payroll JSON payload (or 'demo-clean')")
    p_pdf.add_argument("-o", "--output", required=True, help="Output PDF path")
    p_pdf.add_argument("--watermark", default=None, help="Optional watermark text")

    p_xls = sub.add_parser("build-excel", help="Build macro-free Pro & Free Starter .xlsx workbooks")
    p_xls.add_argument("--out-dir", default="dist_excel", help="Directory for generated .xlsx files")

    args = parser.parse_args(argv)

    def _load(spec_arg: str) -> PayrollSubmission:
        if spec_arg == "demo-clean":
            return build_clean_hvac_subcontractor_sample()
        if spec_arg == "demo-traps":
            return build_buggy_payroll_trap_sample()
        data = json.loads(Path(spec_arg).read_text(encoding="utf-8"))
        return PayrollSubmission.from_dict(data)

    if args.cmd == "audit":
        submission = _load(args.input_json)
        rep = audit_payroll(submission)
        if args.json:
            print(json.dumps(rep.to_dict(), indent=2))
        else:
            verdict = "PASS (0 BLOCKERS — READY TO SIGN)" if rep.passed_submission_gate else f"HOLD ({rep.blocker_count} BLOCKERS)"
            print(f"Submission Gate : {verdict}")
            print(f"Warnings        : {rep.warning_count}")
            print(f"Back Wages Due  : ${rep.total_back_wages_usd:,.2f}")
            print(f"CWHSSA Damages  : ${rep.cwhssa_liquidated_damages_risk_usd:,.2f}")
            for f in rep.findings:
                print(f"  [{f.severity}] {f.rule_id}: {f.title} ({f.cfr_citation})")
                if f.remediation:
                    print(f"      Fix: {f.remediation}")
        return 0 if rep.passed_submission_gate else 2

    if args.cmd == "render-pdf":
        submission = _load(args.input_json)
        out = render_wh347_pdf(submission, args.output, watermark_text=args.watermark)
        print(f"Compiled official DOL WH-347 PDF -> {out}")
        return 0

    if args.cmd == "build-excel":
        out_dir = Path(args.out_dir)
        pro = build_pro_contractor_workbook(out_dir / "ClearWage_WH347_Pro_Contractor_Suite_2026.xlsx")
        free = build_free_starter_workbook(out_dir / "ClearWage_WH347_Starter_Check_2026.xlsx")
        print(f"Generated Pro Suite    -> {pro}")
        print(f"Generated Free Starter -> {free}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
