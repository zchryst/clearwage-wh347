"""Model Context Protocol (MCP) Server for ClearWage WH-347 (DBRA & 2026 Certified Payroll)."""

from __future__ import annotations

import base64
from decimal import Decimal
import tempfile
from pathlib import Path
from typing import Any

from clearwage_wh347.auditor import audit_payroll
from clearwage_wh347.calculator import compute_dbra_overtime_floor
from clearwage_wh347.models import PayrollSubmission, q_cent, to_dec
from clearwage_wh347.pdf_renderer import render_wh347_pdf


def calculate_dbra_overtime_tool(
    wd_basic_hourly_rate: float,
    wd_fringe_hourly_rate: float,
    actual_st_cash_rate_paid: float,
    hourly_plan_credit_claimed: float = 0.0,
    hourly_cash_in_lieu_paid: float = 0.0,
    st_hours: float = 40.0,
    ot_hours: float = 0.0,
) -> dict[str, Any]:
    """Deterministically computes exact DBRA/CWHSSA/FLSA straight-time, overtime, Col 6B, Col 6C, and Col 7A."""
    req_base = to_dec(wd_basic_hourly_rate)
    req_fringe = to_dec(wd_fringe_hourly_rate)
    st_paid = to_dec(actual_st_cash_rate_paid)
    plan_hr = to_dec(hourly_plan_credit_claimed)
    cash_frg_hr = to_dec(hourly_cash_in_lieu_paid)
    st_h = to_dec(st_hours)
    ot_h = to_dec(ot_hours)
    tot_h = st_h + ot_h

    eff_frg = plan_hr + cash_frg_hr
    min_ot_total, min_col6a_ot_cash = compute_dbra_overtime_floor(
        req_base, req_fringe, st_paid, eff_frg
    )
    col_6b = q_cent(tot_h * plan_hr)
    col_6c = q_cent(tot_h * cash_frg_hr)
    col_7a = q_cent(st_h * st_paid + ot_h * min_col6a_ot_cash + col_6c)

    return {
        "required_st_total_package_per_hr": float(req_base + req_fringe),
        "effective_st_total_paid_per_hr": float(st_paid + eff_frg),
        "minimum_col_6a_ot_cash_rate_per_hr": float(min_col6a_ot_cash),
        "minimum_ot_total_package_per_hr": float(min_ot_total),
        "col_6b_total_fringe_benefit_credit_usd": float(col_6b),
        "col_6c_payment_in_lieu_of_fringes_usd": float(col_6c),
        "col_7a_gross_project_earnings_at_min_ot_usd": float(col_7a),
        "compliant_straight_time": (st_paid + eff_frg) >= (req_base + req_fringe),
        "statutory_note": (
            "Per 29 CFR § 5.32 & OMB 1235-0008 (Rev. Jan 2025): Col 6A excludes cash-in-lieu fringes; "
            "OT requires 1.5x regular/WD base cash rate PLUS 1.0x full prevailing fringe rate on all OT hours."
        ),
    }


def audit_wh347_submission_tool(payroll_payload: dict[str, Any]) -> dict[str, Any]:
    """Audits a weekly WH-347 payroll JSON payload against all 26 DBRA, CWHSSA, Copeland Act & 2026 rules."""
    sub = PayrollSubmission.from_dict(payroll_payload)
    rep = audit_payroll(sub)
    return rep.to_dict()


def render_wh347_pdf_base64_tool(
    payroll_payload: dict[str, Any],
    watermark_text: str | None = None,
) -> dict[str, Any]:
    """Compiles a pixel-accurate official DOL Rev. Jan-2025 WH-347 PDF and returns base64 + audit summary."""
    sub = PayrollSubmission.from_dict(payroll_payload)
    rep = audit_payroll(sub)
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = Path(tmp) / "wh347_compiled.pdf"
        render_wh347_pdf(sub, pdf_path, watermark_text=watermark_text)
        b64 = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    return {
        "passed_submission_gate": rep.passed_submission_gate,
        "blocker_count": rep.blocker_count,
        "warning_count": rep.warning_count,
        "pdf_base64": b64,
    }


def build_mcp_server():
    from fastmcp import FastMCP

    mcp = FastMCP(
        "ClearWage-WH347",
        instructions=(
            "Deterministic U.S. Department of Labor Form WH-347 (Rev. Jan 2025, OMB 1235-0008, mandatory Oct 1, 2026) "
            "Davis-Bacon prevailing wage, CWHSSA overtime, fringe benefit Col 6B/6C, and Copeland Act compliance oracle."
        ),
    )

    @mcp.tool()
    def calculate_dbra_overtime(
        wd_basic_hourly_rate: float,
        wd_fringe_hourly_rate: float,
        actual_st_cash_rate_paid: float,
        hourly_plan_credit_claimed: float = 0.0,
        hourly_cash_in_lieu_paid: float = 0.0,
        st_hours: float = 40.0,
        ot_hours: float = 0.0,
    ) -> dict[str, Any]:
        """Compute cent-exact DBRA/FLSA overtime floor and 2026 WH-347 Columns 6B, 6C, and 7A."""
        return calculate_dbra_overtime_tool(
            wd_basic_hourly_rate,
            wd_fringe_hourly_rate,
            actual_st_cash_rate_paid,
            hourly_plan_credit_claimed,
            hourly_cash_in_lieu_paid,
            st_hours,
            ot_hours,
        )

    @mcp.tool()
    def audit_wh347_payroll(payroll_payload: dict[str, Any]) -> dict[str, Any]:
        """Run all 26 statutory DBRA, CWHSSA, Copeland Act & Revised Jan-2025 WH-347 compliance rules."""
        return audit_wh347_submission_tool(payroll_payload)

    @mcp.tool()
    def generate_wh347_official_pdf(
        payroll_payload: dict[str, Any],
        watermark_text: str | None = None,
    ) -> dict[str, Any]:
        """Stamp a pixel-aligned official U.S. DOL Form WH-347 (Rev. Jan 2025) PDF and return base64 bytes."""
        return render_wh347_pdf_base64_tool(payroll_payload, watermark_text=watermark_text)

    return mcp


def main() -> None:
    mcp = build_mcp_server()
    mcp.run()


if __name__ == "__main__":
    main()
