"""Comprehensive unit & integration test suite for ClearWage WH-347."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from openpyxl import load_workbook
import pymupdf

from clearwage_wh347.auditor import audit_payroll
from clearwage_wh347.calculator import compute_dbra_overtime_floor, compute_payroll
from clearwage_wh347.excel_generator import build_free_starter_workbook, build_pro_contractor_workbook
from clearwage_wh347.mcp_server import (
    audit_wh347_submission_tool,
    calculate_dbra_overtime_tool,
    render_wh347_pdf_base64_tool,
)
from clearwage_wh347.models import DeductionItem, FringePlan, WorkerLineInput
from clearwage_wh347.pdf_renderer import render_wh347_pdf
from clearwage_wh347.samples import build_buggy_payroll_trap_sample, build_clean_hvac_subcontractor_sample


class TestClearWageWH347(unittest.TestCase):
    def test_clean_hvac_sample_passes_zero_blockers_and_exact_math(self) -> None:
        sub = build_clean_hvac_subcontractor_sample()
        rep = audit_payroll(sub)
        self.assertTrue(rep.passed_submission_gate, msg=[f.to_dict() for f in rep.findings])
        self.assertEqual(rep.blocker_count, 0)
        self.assertEqual(rep.total_back_wages_usd, Decimal("0.00"))

        calc = rep.computed
        assert calc is not None
        # Worker #1: 40 ST * $39.00 ($1,560) + 4 OT * $58.50 ($234) + $0 cash fringe = $1,794.00
        # Plan credit = 44 hrs * ($8.50 + $4.95 + $0.75 = $14.20/hr) = $624.80
        w1 = calc.lines[0]
        self.assertEqual(w1.total_hours, Decimal("44"))
        self.assertEqual(w1.col_6b_total_fringe_credit, Decimal("624.80"))
        self.assertEqual(w1.col_6c_cash_in_lieu, Decimal("0.00"))
        self.assertEqual(w1.col_7a_gross_project, Decimal("1794.00"))
        # Net pay = 1794.00 - (248.40 + 137.24 + 35.88 = 421.52) = 1372.48
        self.assertEqual(w1.col_9_net_pay, Decimal("1372.48"))

        # Split-classification Worker #2: Row A (24h * $38.50 = $924.00) + Row B (16h * $35.50 = $568.00) = $1,492.00 project gross
        # Plus $310.00 other non-DBRA project gross = $1,802.00 in Col 7B ONLY on primary Row A!
        w2a, w2b = calc.lines[1], calc.lines[2]
        self.assertTrue(w2a.is_primary_row_for_worker)
        self.assertFalse(w2b.is_primary_row_for_worker)
        self.assertEqual(w2a.col_7b_gross_all_work, Decimal("1802.00"))
        self.assertIsNone(w2b.col_7b_gross_all_work)

        # Worker #4: Partial plan ($4.00 * 40 = $160.00 in 6B) + Cash-in-lieu ($3.60 * 40 = $144.00 in 6C)
        # Col 7A = 40 * $22.40 ($896.00) + $144.00 cash fringe = $1,040.00!
        w4 = calc.lines[4]
        self.assertEqual(w4.col_6b_total_fringe_credit, Decimal("160.00"))
        self.assertEqual(w4.col_6c_cash_in_lieu, Decimal("144.00"))
        self.assertEqual(w4.col_7a_gross_project, Decimal("1040.00"))
        # Worker #4 has 2 "Other" deductions -> triggers Copeland Act Addendum!
        self.assertEqual(len(calc.deduction_addendum_rows), 1)

    def test_buggy_trap_sample_catches_all_2026_rejection_traps(self) -> None:
        sub = build_buggy_payroll_trap_sample()
        rep = audit_payroll(sub)
        self.assertFalse(rep.passed_submission_gate)
        rule_ids = {f.rule_id for f in rep.findings}
        # Must catch: missing WD# (003), full SSN (007), cash fringe in 6A (014),
        # unregistered RA (013), prevailing ST shortfall (016), and CWHSSA >40h (019)!
        for expected in ("WH347-003", "WH347-007", "WH347-013", "WH347-014", "WH347-016", "WH347-019"):
            self.assertIn(expected, rule_ids)
        self.assertGreater(rep.total_back_wages_usd, Decimal("150.00"))
        self.assertGreater(rep.cwhssa_liquidated_damages_risk_usd, Decimal("0.00"))

    def test_page2_na_rule_and_100pct_cash_in_lieu_rule(self) -> None:
        sub = build_clean_hvac_subcontractor_sample()
        # Remove apprentice and switch everyone to 100% cash-in-lieu (0 plan credits)
        sub.apprentice_programs = []
        sub.worker_lines = [sub.worker_lines[4]]
        sub.worker_lines[0].worker_entry_no = 1
        sub.worker_lines[0].plan_hourly_credits = {}
        sub.worker_lines[0].cash_in_lieu_hourly_rate = Decimal("7.60")
        sub.worker_deductions = {}
        calc = compute_payroll(sub)
        self.assertFalse(calc.box4_apprentices_checked)
        self.assertTrue(calc.apprentice_table_na)
        self.assertTrue(calc.box5_fringes_checked)
        # Per DOL instructions: 100% cash-in-lieu checks Box 5 but leaves Page 2 hourly grid blank!
        self.assertFalse(calc.populate_page2_fringe_grid)

    def test_unfunded_fringe_plan_without_dol_approval_is_blocked(self) -> None:
        sub = build_clean_hvac_subcontractor_sample()
        sub.fringe_plans.append(
            FringePlan("FB4", "Self-Insured Shop PTO", "Vacation", "PTO-1", is_funded=False, dol_unfunded_approval_ref="")
        )
        rep = audit_payroll(sub)
        self.assertIn("WH347-021", {f.rule_id for f in rep.findings})

    def test_dbra_overtime_floor_handles_higher_actual_regular_rate(self) -> None:
        # WD Base = $30, WD Fringe = $10 (Total ST = $40).
        # Contractor pays $36 cash ST + $10 fringe.
        # Under FLSA + DBRA, cash OT must be 1.5 * $36 = $54, plus $10 fringe = $64/hr!
        tot_ot, cash_ot = compute_dbra_overtime_floor(
            Decimal("30.00"), Decimal("10.00"), Decimal("36.00"), Decimal("10.00")
        )
        self.assertEqual(cash_ot, Decimal("54.00"))
        self.assertEqual(tot_ot, Decimal("64.00"))

    def test_pdf_overlay_compiler_produces_verified_3page_packet(self) -> None:
        sub = build_clean_hvac_subcontractor_sample()
        with tempfile.TemporaryDirectory() as tmp:
            out_pdf = Path(tmp) / "wh347_test.pdf"
            render_wh347_pdf(sub, out_pdf)
            self.assertTrue(out_pdf.exists())
            doc = pymupdf.open(str(out_pdf))
            # Page 1 + Page 2 + Copeland Act Deductions Addendum = 3 pages!
            self.assertEqual(len(doc), 3)
            p1_txt = doc[0].get_text()
            p2_txt = doc[1].get_text()
            p3_txt = doc[2].get_text()
            self.assertIn("VA Outpatient Surgical Wing", p1_txt)
            self.assertIn("TX20260028 Mod 3", p1_txt)
            self.assertIn("Ramirez", p1_txt)
            self.assertIn("1,794.00", p1_txt)
            self.assertIn("Elena M. Vance", p2_txt)
            self.assertIn("Austin Electrical JATC", p2_txt)
            self.assertIn("COPELAND ACT", p3_txt)
            doc.close()

    def test_excel_suite_generators_produce_valid_macro_free_workbooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pro_path = build_pro_contractor_workbook(Path(tmp) / "pro.xlsx")
            free_path = build_free_starter_workbook(Path(tmp) / "starter.xlsx")
            wb_pro = load_workbook(pro_path, data_only=False)
            self.assertEqual(len(wb_pro.sheetnames), 6)
            ws_ent = wb_pro["3_Weekly_Crew_Entry"]
            self.assertTrue(str(ws_ent["AF5"].value).startswith("=IF("))
            wb_free = load_workbook(free_path, data_only=False)
            self.assertEqual(wb_free.sheetnames, ["WH347_2026_Free_QuickCheck"])

    def test_mcp_tools_roundtrip(self) -> None:
        ot_res = calculate_dbra_overtime_tool(38.50, 14.20, 39.00, 14.20, 0.0, 40, 4)
        self.assertTrue(ot_res["compliant_straight_time"])
        self.assertEqual(ot_res["minimum_col_6a_ot_cash_rate_per_hr"], 58.5)
        self.assertEqual(ot_res["col_6b_total_fringe_benefit_credit_usd"], 624.8)

        # Build minimal JSON dict and verify MCP audit + PDF base64 tool
        payload = {
            "project_name": "Federal Courthouse Roof",
            "project_no": "GS-07P-26-009",
            "certified_payroll_no": 1,
            "contractor_role": "subcontractor",
            "business_name": "Apex Roofing Inc.",
            "business_address": "100 Main St, Dallas, TX",
            "project_location": "Dallas, Dallas County, TX",
            "wage_determination_no": "TX20260011 Mod 1",
            "week_ending_date": "2026-10-24",
            "certifying_official_name": "Jane Doe",
            "certifying_official_title": "President",
            "telephone": "214-555-0100",
            "email": "jane@apex-example.com",
            "wage_determinations": [{"classification": "Roofer", "basic_hourly_rate": "28.00", "fringe_hourly_rate": "6.50"}],
            "worker_lines": [
                {
                    "worker_entry_no": 1,
                    "last_name": "Smith",
                    "first_name": "John",
                    "worker_id": "1122",
                    "status": "J",
                    "labor_classification": "Roofer",
                    "st_hours": [0, 8, 8, 8, 8, 8, 0],
                    "ot_hours": [0, 0, 0, 0, 0, 0, 0],
                    "st_rate_paid": "28.00",
                    "ot_rate_paid": "42.00",
                    "cash_in_lieu_hourly_rate": "6.50",
                }
            ],
        }
        aud = audit_wh347_submission_tool(payload)
        self.assertTrue(aud["passed_submission_gate"])
        pdf_res = render_wh347_pdf_base64_tool(payload)
        self.assertTrue(len(pdf_res["pdf_base64"]) > 10000)


if __name__ == "__main__":
    unittest.main()
