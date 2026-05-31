"""
AfCFTA Product-Specific Rules of Origin — Annex 2 to the Protocol on Trade in Goods
Source: African Union, African Continental Free Trade Area Agreement

AfCFTA uses a "change in tariff classification" plus RVC approach.
The default rule for manufactured goods is:
  - Change in Chapter (CC) OR
  - RVC ≥ 35% (Build-Up method, called "value added content" in AfCFTA text)

Agriculture and natural resources: wholly obtained.
Textiles: yarn-forward (similar to CUSMA).

Note: AfCFTA PSRs are in active development (Phase 1 goods). Phase 2 (services/investment)
rules are pending. This file covers goods traded under Phase 1 schedules.

Source: https://au-afcfta.org/agreements/
"""

# (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
#  sec_type, sec_threshold, sec_rvc, source_ref, is_default)
AFCFTA_RULES = [

    # ─── Section I — Live Animals ──────────────────────────────────────────────

    ("01", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.01", True),
    ("02", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.02", True),
    ("03", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.03", True),
    ("04", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.04", True),
    ("05", "tariff_shift",
     "A change to any heading of Chapter 5 from any other heading.",
     None, None, "heading", None, None, None, "AfCFTA Annex 2, Ch.05", True),

    # ─── Section II — Vegetable Products ──────────────────────────────────────

    ("06", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.06", True),
    ("07", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.07", True),
    ("08", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.08", True),
    ("09", "combined",
     "A change to any heading of Chapter 9 from any other chapter; or value added content (VAC) not less than 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.09", True),
    ("10", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.10", True),
    ("11", "combined",
     "A change to any heading of Chapter 11 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.11", True),
    ("12", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.12", True),
    ("13", "combined",
     "A change to any heading of Chapter 13 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.13", True),
    ("14", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.14", True),

    # ─── Section III ───────────────────────────────────────────────────────────

    ("15", "combined",
     "A change to any heading of Chapter 15 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.15", True),

    # ─── Section IV — Prepared Foods ──────────────────────────────────────────

    ("16", "combined",
     "A change to any heading of Chapter 16 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.16", True),
    ("17", "combined",
     "A change to any heading of Chapter 17 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.17", True),
    ("18", "combined",
     "A change to any heading of Chapter 18 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.18", True),
    ("19", "combined",
     "A change to any heading of Chapter 19 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.19", True),
    ("20", "combined",
     "A change to any heading of Chapter 20 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.20", True),
    ("21", "combined",
     "A change to any heading of Chapter 21 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.21", True),
    ("22", "combined",
     "A change to any heading of Chapter 22 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.22", True),
    ("23", "combined",
     "A change to any heading of Chapter 23 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.23", True),
    ("24", "combined",
     "A change to any heading of Chapter 24 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.24", True),

    # ─── Section V — Minerals ─────────────────────────────────────────────────

    ("25", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.25", True),
    ("26", "wholly_obtained",
     "Wholly obtained or produced within the territory of a State Party.",
     None, None, None, None, None, None, "AfCFTA Annex 2, Ch.26", True),
    ("27", "combined",
     "A change to any heading of Chapter 27 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.27", True),

    # ─── Section VI — Chemicals ────────────────────────────────────────────────

    ("28", "combined",
     "A change to any heading of Chapter 28 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.28", True),
    ("29", "combined",
     "A change to any heading of Chapter 29 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.29", True),
    ("30", "combined",
     "A change to any heading of Chapter 30 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.30", True),
    ("31", "combined",
     "A change to any heading of Chapter 31 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.31", True),
    ("32", "combined",
     "A change to any heading of Chapter 32 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.32", True),
    ("33", "combined",
     "A change to any heading of Chapter 33 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.33", True),
    ("34", "combined",
     "A change to any heading of Chapter 34 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.34", True),
    ("35", "combined",
     "A change to any heading of Chapter 35 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.35", True),
    ("36", "combined",
     "A change to any heading of Chapter 36 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.36", True),
    ("37", "combined",
     "A change to any heading of Chapter 37 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.37", True),
    ("38", "combined",
     "A change to any heading of Chapter 38 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.38", True),

    # ─── Section VII ───────────────────────────────────────────────────────────

    ("39", "combined",
     "A change to any heading of Chapter 39 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.39", True),
    ("40", "combined",
     "A change to any heading of Chapter 40 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.40", True),

    # ─── Section VIII ──────────────────────────────────────────────────────────

    ("41", "combined",
     "A change to any heading of Chapter 41 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.41", True),
    ("42", "combined",
     "A change to any heading of Chapter 42 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.42", True),
    ("43", "combined",
     "A change to any heading of Chapter 43 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.43", True),

    # ─── Section IX ────────────────────────────────────────────────────────────

    ("44", "combined",
     "A change to any heading of Chapter 44 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.44", True),
    ("45", "combined",
     "A change to any heading of Chapter 45 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.45", True),
    ("46", "combined",
     "A change to any heading of Chapter 46 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.46", True),
    ("47", "combined",
     "A change to any heading of Chapter 47 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.47", True),
    ("48", "combined",
     "A change to any heading of Chapter 48 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.48", True),
    ("49", "combined",
     "A change to any heading of Chapter 49 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.49", True),

    # ─── Section XI — Textiles ─────────────────────────────────────────────────
    # AfCFTA textiles: CC (yarn-forward) or VAC ≥ 35%

    ("50", "combined",
     "A change to any heading of Chapter 50 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.50", True),
    ("51", "combined",
     "A change to any heading of Chapter 51 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.51", True),
    ("52", "combined",
     "A change to any heading of Chapter 52 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.52", True),
    ("53", "combined",
     "A change to any heading of Chapter 53 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.53", True),
    ("54", "combined",
     "A change to any heading of Chapter 54 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.54", True),
    ("55", "combined",
     "A change to any heading of Chapter 55 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.55", True),
    ("56", "combined",
     "A change to any heading of Chapter 56 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.56", True),
    ("57", "combined",
     "A change to any heading of Chapter 57 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.57", True),
    ("58", "combined",
     "A change to any heading of Chapter 58 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.58", True),
    ("59", "combined",
     "A change to any heading of Chapter 59 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.59", True),
    ("60", "combined",
     "A change to any heading of Chapter 60 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.60", True),
    ("61", "combined",
     "A change to any heading of Chapter 61 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.61", True),
    ("62", "combined",
     "A change to any heading of Chapter 62 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.62", True),
    ("63", "combined",
     "A change to any heading of Chapter 63 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.63", True),

    # ─── Section XII ───────────────────────────────────────────────────────────

    ("64", "combined",
     "A change to any heading of Chapter 64 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.64", True),
    ("65", "combined",
     "A change to any heading of Chapter 65 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.65", True),
    ("66", "combined",
     "A change to any heading of Chapter 66 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.66", True),
    ("67", "combined",
     "A change to any heading of Chapter 67 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.67", True),

    # ─── Section XIII ──────────────────────────────────────────────────────────

    ("68", "combined",
     "A change to any heading of Chapter 68 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.68", True),
    ("69", "combined",
     "A change to any heading of Chapter 69 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.69", True),
    ("70", "combined",
     "A change to any heading of Chapter 70 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.70", True),

    # ─── Section XIV ───────────────────────────────────────────────────────────

    ("71", "combined",
     "A change to any heading of Chapter 71 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.71", True),

    # ─── Section XV — Base Metals ─────────────────────────────────────────────

    ("72", "combined",
     "A change to any heading of Chapter 72 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.72", True),
    ("73", "combined",
     "A change to any heading of Chapter 73 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.73", True),
    ("74", "combined",
     "A change to any heading of Chapter 74 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.74", True),
    ("75", "combined",
     "A change to any heading of Chapter 75 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.75", True),
    ("76", "combined",
     "A change to any heading of Chapter 76 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.76", True),
    ("78", "combined",
     "A change to any heading of Chapter 78 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.78", True),
    ("79", "combined",
     "A change to any heading of Chapter 79 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.79", True),
    ("80", "combined",
     "A change to any heading of Chapter 80 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.80", True),
    ("81", "combined",
     "A change to any heading of Chapter 81 from any other chapter; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "chapter", None, None, None, "AfCFTA Annex 2, Ch.81", True),
    ("82", "combined",
     "A change to any heading of Chapter 82 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.82", True),
    ("83", "combined",
     "A change to any heading of Chapter 83 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.83", True),

    # ─── Section XVI — Machinery ───────────────────────────────────────────────

    ("84", "combined",
     "A change to any heading of Chapter 84 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.84", True),
    ("85", "combined",
     "A change to any heading of Chapter 85 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.85", True),

    # ─── Section XVII — Vehicles ───────────────────────────────────────────────

    ("86", "combined",
     "A change to any heading of Chapter 86 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.86", True),

    # Vehicles — AfCFTA sets RVC ≥ 35% VAC (Build-Up) for all vehicles
    ("8703", "rvc_build_up",
     "VAC (Value Added Content) ≥ 35% of ex-factory price.",
     35.0, "build_up", None, None, None, None,
     "AfCFTA Annex 2, Ch.87 (8703)", False),
    ("8704", "rvc_build_up",
     "VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", None, None, None, None,
     "AfCFTA Annex 2, Ch.87 (8704)", False),
    ("8708", "rvc_build_up",
     "VAC ≥ 35% of ex-factory price; or a change to heading 87.08 from any other heading.",
     35.0, "build_up", None, None, None, None,
     "AfCFTA Annex 2, Ch.87 (8708)", False),
    ("87", "combined",
     "A change to any heading of Chapter 87 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.87", True),

    ("88", "combined",
     "A change to any heading of Chapter 88 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.88", True),
    ("89", "combined",
     "A change to any heading of Chapter 89 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.89", True),

    # ─── Section XVIII ─────────────────────────────────────────────────────────

    ("90", "combined",
     "A change to any heading of Chapter 90 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.90", True),
    ("91", "combined",
     "A change to any heading of Chapter 91 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.91", True),
    ("92", "combined",
     "A change to any heading of Chapter 92 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.92", True),

    # ─── Section XIX ───────────────────────────────────────────────────────────

    ("93", "combined",
     "A change to any heading of Chapter 93 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.93", True),

    # ─── Section XX ────────────────────────────────────────────────────────────

    ("94", "combined",
     "A change to any heading of Chapter 94 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.94", True),
    ("95", "combined",
     "A change to any heading of Chapter 95 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.95", True),
    ("96", "combined",
     "A change to any heading of Chapter 96 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.96", True),

    # ─── Section XXI ───────────────────────────────────────────────────────────

    ("97", "combined",
     "A change to any heading of Chapter 97 from any other heading; or VAC ≥ 35% of ex-factory price.",
     35.0, "build_up", "heading", None, None, None, "AfCFTA Annex 2, Ch.97", True),
]

COLUMNS = [
    "hs_code", "rule_type", "rule_text", "value_threshold", "rvc_method",
    "ts_heading_level", "secondary_rule_type", "secondary_value_threshold",
    "secondary_rvc_method", "source_reference", "is_default",
]
