"""Realistic federal subcontractor payroll fixtures (clean & rejection-trap scenarios)."""

from __future__ import annotations

from decimal import Decimal

from clearwage_wh347.models import (
    ApprenticeProgram,
    DeductionItem,
    FringePlan,
    PayrollSubmission,
    WageDeterminationRate,
    WorkerAllWorkDeductions,
    WorkerLineInput,
)


def build_clean_hvac_subcontractor_sample() -> PayrollSubmission:
    """Returns a 100% compliant Revised Jan-2025 WH-347 HVAC/Electrical subcontractor filing."""
    return PayrollSubmission(
        project_name="VA Outpatient Surgical Wing MEP Modernization",
        project_no="36C257-26-C-0114",
        certified_payroll_no=4,
        contractor_role="subcontractor",
        business_name="Lone Star Mechanical & Controls LLC",
        business_address="4820 Burnet Rd, Suite 210, Austin, TX 78756",
        project_location="7901 Metropolis Dr, Austin, Travis County, TX 78744",
        wage_determination_no="TX20260028 Mod 3 (Building)",
        week_ending_date="2026-10-24",
        certifying_official_name="Elena M. Vance",
        certifying_official_title="Payroll & Compliance Manager",
        is_final_payroll=False,
        cwhssa_applies=True,
        signature_text="/s/ Elena M. Vance",
        signature_date="2026-10-27",
        telephone="(512) 555-0194",
        email="compliance@lonestarmech-example.com",
        additional_remarks="All electronic timecards reconciled against GC daily sign-in logs.",
        wage_determinations=[
            WageDeterminationRate("Electrician (Inside Wireman)", Decimal("38.50"), Decimal("14.20")),
            WageDeterminationRate("HVAC Sheet Metal Mechanic", Decimal("35.00"), Decimal("12.80")),
            WageDeterminationRate("Laborer - Common / General", Decimal("22.40"), Decimal("7.60")),
        ],
        apprentice_programs=[
            ApprenticeProgram(
                program_name="Austin Electrical JATC Local 520",
                registration_agency="OA",
                labor_classification="Electrician (Inside Wireman)",
                journeyworker_classification="Electrician (Inside Wireman)",
                progression_pct=Decimal("65"),
                fringes_full_rate=True,
                ratio_apprentices=1,
                ratio_journeyworkers=1,
            )
        ],
        fringe_plans=[
            FringePlan("FB1", "IBEW/NECA Health & Welfare", "Medical/Dental", "HW-520-A", is_funded=True),
            FringePlan("FB2", "NEBF National Pension Trust", "Defined Benefit", "PN-001", is_funded=True),
            FringePlan("FB3", "JATC Apprenticeship Training", "Apprenticeship", "TR-520", is_funded=True),
        ],
        worker_lines=[
            # Worker #1: Journeyworker Electrician with 40 ST + 4 OT hrs
            WorkerLineInput(
                worker_entry_no=1,
                last_name="Ramirez",
                first_name="Carlos",
                middle_initial="A",
                worker_id="4829",
                status="J",
                labor_classification="Electrician (Inside Wireman)",
                st_hours=[Decimal("0"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("0")],
                ot_hours=[Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("2"), Decimal("2")],
                st_rate_paid=Decimal("39.00"),
                ot_rate_paid=Decimal("58.50"),
                plan_hourly_credits={"FB1": Decimal("8.50"), "FB2": Decimal("4.95"), "FB3": Decimal("0.75")},
                cash_in_lieu_hourly_rate=Decimal("0.00"),
            ),
            # Worker #2 (Row A): Split-classification worker! 24 hrs Electrician...
            WorkerLineInput(
                worker_entry_no=2,
                last_name="Chen",
                first_name="Marcus",
                middle_initial="L",
                worker_id="9104",
                status="J",
                labor_classification="Electrician (Inside Wireman)",
                st_hours=[Decimal("0"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("0"), Decimal("0"), Decimal("0")],
                ot_hours=[Decimal("0")] * 7,
                st_rate_paid=Decimal("38.50"),
                ot_rate_paid=Decimal("57.75"),
                plan_hourly_credits={"FB1": Decimal("8.50"), "FB2": Decimal("4.95"), "FB3": Decimal("0.75")},
                cash_in_lieu_hourly_rate=Decimal("0.00"),
            ),
            # Worker #2 (Row B): ...and 16 hrs HVAC Sheet Metal Mechanic on SAME Entry #2!
            WorkerLineInput(
                worker_entry_no=2,
                last_name="Chen",
                first_name="Marcus",
                middle_initial="L",
                worker_id="9104",
                status="J",
                labor_classification="HVAC Sheet Metal Mechanic",
                st_hours=[Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("8"), Decimal("8"), Decimal("0")],
                ot_hours=[Decimal("0")] * 7,
                st_rate_paid=Decimal("35.50"),
                ot_rate_paid=Decimal("53.25"),
                plan_hourly_credits={"FB1": Decimal("8.50"), "FB2": Decimal("4.30"), "FB3": Decimal("0.00")},
                cash_in_lieu_hourly_rate=Decimal("0.00"),
            ),
            # Worker #3: Registered Apprentice (65% of $38.50 = $25.03 base + $14.20 full fringe)
            WorkerLineInput(
                worker_entry_no=3,
                last_name="Brooks",
                first_name="Devin",
                middle_initial="T",
                worker_id="7731",
                status="RA",
                apprentice_progression="Per. 3 (65%)",
                apprentice_program_name="Austin Electrical JATC Local 520",
                labor_classification="Electrician (Inside Wireman)",
                st_hours=[Decimal("0"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("0")],
                ot_hours=[Decimal("0")] * 7,
                st_rate_paid=Decimal("25.50"),
                ot_rate_paid=Decimal("38.25"),
                plan_hourly_credits={"FB1": Decimal("8.50"), "FB2": Decimal("4.95"), "FB3": Decimal("0.75")},
                cash_in_lieu_hourly_rate=Decimal("0.00"),
            ),
            # Worker #4: General Laborer paid partial plan credit ($4.00/hr) + Cash-in-Lieu ($3.60/hr = $7.60 fringe)
            WorkerLineInput(
                worker_entry_no=4,
                last_name="Kowalski",
                first_name="Tomasz",
                middle_initial="",
                worker_id="3318",
                status="J",
                labor_classification="Laborer - Common / General",
                st_hours=[Decimal("0"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("0")],
                ot_hours=[Decimal("0")] * 7,
                st_rate_paid=Decimal("22.40"),
                ot_rate_paid=Decimal("33.60"),
                plan_hourly_credits={"FB1": Decimal("4.00")},
                cash_in_lieu_hourly_rate=Decimal("3.60"),
            ),
        ],
        worker_deductions={
            1: WorkerAllWorkDeductions(
                worker_entry_no=1,
                other_projects_gross=Decimal("0.00"),
                tax_withholdings=Decimal("248.40"),
                fica=Decimal("137.24"),
                other_deductions=[DeductionItem("IBEW Working Dues (29 CFR 3.5(i))", Decimal("35.88"))],
            ),
            2: WorkerAllWorkDeductions(
                worker_entry_no=2,
                other_projects_gross=Decimal("310.00"),  # Worked 8 hrs on commercial non-DBRA job
                tax_withholdings=Decimal("231.10"),
                fica=Decimal("137.85"),
                other_deductions=[],
            ),
            3: WorkerAllWorkDeductions(
                worker_entry_no=3,
                other_projects_gross=Decimal("0.00"),
                tax_withholdings=Decimal("112.00"),
                fica=Decimal("78.03"),
                other_deductions=[],
            ),
            4: WorkerAllWorkDeductions(
                worker_entry_no=4,
                other_projects_gross=Decimal("0.00"),
                tax_withholdings=Decimal("108.50"),
                fica=Decimal("79.56"),
                other_deductions=[
                    DeductionItem("Court-Ordered Child Support Order #TX-8841", Decimal("125.00")),
                    DeductionItem("Voluntary 401(k) Employee Deferral", Decimal("52.00")),
                ],
            ),
        },
    )


def build_buggy_payroll_trap_sample() -> PayrollSubmission:
    """Returns a realistic broken payroll containing 6 common Oct-2026 rejection errors."""
    sub = build_clean_hvac_subcontractor_sample()
    sub.wage_determination_no = ""  # Trap 1: Missing new 2025 Wage Determination No. header
    # Trap 2: Full 9-digit SSN in Col 1E on Worker #1 + Cash-in-lieu mixed into Col 6A
    sub.worker_lines[0].worker_id = "459-82-4829"
    sub.worker_lines[0].includes_cash_fringe_in_6a = True
    # Trap 3: Worker #4 logged 46 ST hours and 0 OT hours (CWHSSA >40 hr violation) + $2.00/hr fringe shortfall
    sub.worker_lines[4].st_hours = [Decimal("0"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("8"), Decimal("6")]
    sub.worker_lines[4].cash_in_lieu_hourly_rate = Decimal("1.60")
    # Trap 4: Apprentice missing OA/SAA program registration
    sub.apprentice_programs = []
    return sub
