"""
CPTPP Product-Specific Rules of Origin — Annex 3-D
Source: Comprehensive and Progressive Agreement for Trans-Pacific Partnership

CPTPP rules are largely similar to TPP (which was based on NAFTA/TPP negotiations).
RVC is calculated on Adjusted Value (AV), essentially FOB/ex-works value.
Build-Down: RVC = (AV - VNM) / AV × 100
Net Cost: RVC = (NC - VNM) / NC × 100
General threshold: 40% BD or 30% NC.
"""

# (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
#  sec_type, sec_threshold, sec_rvc, source_ref, is_default)
CPTPP_RULES = [

    # ─── Section I ─────────────────────────────────────────────────────────────

    ("01", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.01", True),
    ("02", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.02", True),
    ("03", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.03", True),
    ("04", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.04", True),
    ("05", "tariff_shift",
     "CTH — A change to any heading of Chapter 5 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.05", True),

    # ─── Section II ────────────────────────────────────────────────────────────

    ("06", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.06", True),
    ("07", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.07", True),
    ("08", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.08", True),
    ("09", "tariff_shift",
     "CTH — A change to any heading of Chapter 9 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.09", True),
    ("10", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.10", True),
    ("11", "tariff_shift",
     "CTH — A change to any heading of Chapter 11 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.11", True),
    ("12", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.12", True),
    ("13", "tariff_shift",
     "CTH — A change to any heading of Chapter 13 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.13", True),
    ("14", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.14", True),

    # ─── Section III ───────────────────────────────────────────────────────────

    ("15", "tariff_shift",
     "CTH — A change to any heading of Chapter 15 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.15", True),

    # ─── Section IV ────────────────────────────────────────────────────────────

    ("16", "tariff_shift",
     "CTH — A change to any heading of Chapter 16 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.16", True),
    ("17", "tariff_shift",
     "CTH — A change to any heading of Chapter 17 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.17", True),
    ("18", "tariff_shift",
     "CTH — A change to any heading of Chapter 18 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.18", True),
    ("19", "tariff_shift",
     "CTH — A change to any heading of Chapter 19 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.19", True),
    ("20", "tariff_shift",
     "CTH — A change to any heading of Chapter 20 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.20", True),
    ("21", "tariff_shift",
     "CTH — A change to any heading of Chapter 21 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.21", True),
    ("22", "tariff_shift",
     "CTH — A change to any heading of Chapter 22 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.22", True),
    ("23", "tariff_shift",
     "CTH — A change to any heading of Chapter 23 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.23", True),
    ("24", "tariff_shift",
     "CTH — A change to any heading of Chapter 24 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.24", True),

    # ─── Section V — Minerals ─────────────────────────────────────────────────

    ("25", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.25", True),
    ("26", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CPTPP Annex 3-D, Ch.26", True),
    ("27", "tariff_shift",
     "CTH — A change to any heading of Chapter 27 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.27", True),

    # ─── Section VI — Chemicals ────────────────────────────────────────────────

    ("28", "combined",
     "CTH — A change to any heading of Chapter 28 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.28", True),
    ("29", "combined",
     "CTH — A change to any heading of Chapter 29 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.29", True),
    ("30", "combined",
     "CTH — A change to any heading of Chapter 30 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.30", True),
    ("31", "tariff_shift",
     "CTH — A change to any heading of Chapter 31 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.31", True),
    ("32", "combined",
     "CTH — A change to any heading of Chapter 32 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.32", True),
    ("33", "combined",
     "CTH — A change to any heading of Chapter 33 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.33", True),
    ("34", "combined",
     "CTH — A change to any heading of Chapter 34 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.34", True),
    ("35", "combined",
     "CTH — A change to any heading of Chapter 35 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.35", True),
    ("36", "tariff_shift",
     "CTH — A change to any heading of Chapter 36 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.36", True),
    ("37", "combined",
     "CTH — A change to any heading of Chapter 37 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.37", True),
    ("38", "combined",
     "CTH — A change to any heading of Chapter 38 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.38", True),

    # ─── Section VII ───────────────────────────────────────────────────────────

    ("39", "combined",
     "CTH — A change to any heading of Chapter 39 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.39", True),
    ("40", "combined",
     "CTH — A change to any heading of Chapter 40 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.40", True),

    # ─── Section VIII ──────────────────────────────────────────────────────────

    ("41", "tariff_shift",
     "CTH — A change to any heading of Chapter 41 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.41", True),
    ("42", "combined",
     "CTH — A change to any heading of Chapter 42 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.42", True),
    ("43", "tariff_shift",
     "CTH — A change to any heading of Chapter 43 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.43", True),

    # ─── Section IX ────────────────────────────────────────────────────────────

    ("44", "tariff_shift",
     "CTH — A change to any heading of Chapter 44 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.44", True),
    ("45", "tariff_shift",
     "CTH — A change to any heading of Chapter 45 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.45", True),
    ("46", "tariff_shift",
     "CTH — A change to any heading of Chapter 46 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.46", True),
    ("47", "tariff_shift",
     "CTH — A change to any heading of Chapter 47 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.47", True),
    ("48", "combined",
     "CTH — A change to any heading of Chapter 48 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.48", True),
    ("49", "tariff_shift",
     "CTH — A change to any heading of Chapter 49 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.49", True),

    # ─── Section XI — Textiles ─────────────────────────────────────────────────
    # CPTPP: yarn-forward for most apparel; fabric-forward for some made-up articles.

    ("50", "tariff_shift",
     "CC — A change to any heading of Chapter 50 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.50", True),
    ("51", "tariff_shift",
     "CC — A change to any heading of Chapter 51 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.51", True),
    ("52", "tariff_shift",
     "CC — A change to any heading of Chapter 52 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.52", True),
    ("53", "tariff_shift",
     "CC — A change to any heading of Chapter 53 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.53", True),
    ("54", "tariff_shift",
     "CC — A change to any heading of Chapter 54 from any other chapter, except from heading 54.02 through 54.05.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.54", True),
    ("55", "tariff_shift",
     "CC — A change to any heading of Chapter 55 from any other chapter, except from headings 55.01 through 55.07.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.55", True),
    ("56", "tariff_shift",
     "CC — A change to any heading of Chapter 56 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.56", True),
    ("57", "tariff_shift",
     "CC — A change to any heading of Chapter 57 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.57", True),
    ("58", "tariff_shift",
     "CC — A change to any heading of Chapter 58 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.58", True),
    ("59", "tariff_shift",
     "CC — A change to any heading of Chapter 59 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.59", True),
    ("60", "tariff_shift",
     "CC — A change to any heading of Chapter 60 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.60", True),
    ("61", "tariff_shift",
     "CC — A change to any heading of Chapter 61 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.61", True),
    ("62", "tariff_shift",
     "CC — A change to any heading of Chapter 62 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.62", True),
    ("63", "combined",
     "CTH — A change to any heading of Chapter 63 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.63", True),

    # ─── Section XII ───────────────────────────────────────────────────────────

    ("64", "tariff_shift",
     "CTH — A change to any heading of Chapter 64 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.64", True),
    ("65", "tariff_shift",
     "CTH — A change to any heading of Chapter 65 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.65", True),
    ("66", "tariff_shift",
     "CTH — A change to any heading of Chapter 66 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.66", True),
    ("67", "tariff_shift",
     "CTH — A change to any heading of Chapter 67 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.67", True),

    # ─── Section XIII ──────────────────────────────────────────────────────────

    ("68", "combined",
     "CTH — A change to any heading of Chapter 68 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.68", True),
    ("69", "combined",
     "CTH — A change to any heading of Chapter 69 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.69", True),
    ("70", "combined",
     "CTH — A change to any heading of Chapter 70 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.70", True),

    # ─── Section XIV ───────────────────────────────────────────────────────────

    ("71", "combined",
     "CTH — A change to any heading of Chapter 71 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.71", True),

    # ─── Section XV — Base Metals ─────────────────────────────────────────────

    ("72", "tariff_shift",
     "CTH — A change to any heading of Chapter 72 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.72", True),
    ("73", "combined",
     "CTH — A change to any heading of Chapter 73 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.73", True),
    ("74", "tariff_shift",
     "CTH — A change to any heading of Chapter 74 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.74", True),
    ("75", "tariff_shift",
     "CTH — A change to any heading of Chapter 75 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.75", True),
    ("76", "tariff_shift",
     "CTH — A change to any heading of Chapter 76 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.76", True),
    ("78", "tariff_shift",
     "CTH — A change to any heading of Chapter 78 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.78", True),
    ("79", "tariff_shift",
     "CTH — A change to any heading of Chapter 79 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.79", True),
    ("80", "tariff_shift",
     "CTH — A change to any heading of Chapter 80 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.80", True),
    ("81", "tariff_shift",
     "CTH — A change to any heading of Chapter 81 from any other chapter.",
     None, None, "chapter", None, None, None, "CPTPP Annex 3-D, Ch.81", True),
    ("82", "combined",
     "CTH — A change to any heading of Chapter 82 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.82", True),
    ("83", "combined",
     "CTH — A change to any heading of Chapter 83 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.83", True),

    # ─── Section XVI — Machinery ───────────────────────────────────────────────

    ("84", "combined",
     "CTH — A change to any heading of Chapter 84 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.84", True),
    ("85", "combined",
     "CTH — A change to any heading of Chapter 85 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.85", True),

    # Telephones (8517) — RVC ≥ 40% BD or 30% NC
    ("8517", "rvc_build_down",
     "RVC ≥ 40% (Build-Down method) or 30% (Net Cost method).",
     40.0, "build_down", None, "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.85 (8517)", False),

    # Semiconductors (8542) — CTH or RVC ≥ 40%
    ("8542", "combined",
     "CTH — A change to heading 85.42 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.85 (8542)", False),

    # ─── Section XVII — Vehicles ───────────────────────────────────────────────

    ("86", "combined",
     "CTH — A change to any heading of Chapter 86 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.86", True),

    # Passenger vehicles (8703) — RVC ≥ 40% BD or 30% NC
    ("8703", "rvc_build_down",
     "RVC ≥ 40% (Build-Down method) or 30% (Net Cost method).",
     40.0, "build_down", None, "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.87 (8703)", False),

    # Trucks (8704) — RVC ≥ 40% BD or 30% NC
    ("8704", "rvc_build_down",
     "RVC ≥ 40% (Build-Down method) or 30% (Net Cost method).",
     40.0, "build_down", None, "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.87 (8704)", False),

    # Auto parts (8708) — RVC ≥ 40% BD or 30% NC
    ("8708", "rvc_build_down",
     "RVC ≥ 40% (Build-Down method) or 30% (Net Cost method).",
     40.0, "build_down", None, "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.87 (8708)", False),

    # Ch 87 default
    ("87", "combined",
     "CTH — A change to any heading of Chapter 87 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.87", True),

    ("88", "combined",
     "CTH — A change to any heading of Chapter 88 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.88", True),

    ("89", "combined",
     "CTH — A change to any heading of Chapter 89 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.89", True),

    # ─── Section XVIII ─────────────────────────────────────────────────────────

    ("90", "combined",
     "CTH — A change to any heading of Chapter 90 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.90", True),
    ("91", "combined",
     "CTH — A change to any heading of Chapter 91 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.91", True),
    ("92", "combined",
     "CTH — A change to any heading of Chapter 92 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.92", True),

    # ─── Section XIX ───────────────────────────────────────────────────────────

    ("93", "tariff_shift",
     "CTH — A change to any heading of Chapter 93 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.93", True),

    # ─── Section XX ────────────────────────────────────────────────────────────

    ("94", "combined",
     "CTH — A change to any heading of Chapter 94 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.94", True),
    ("95", "combined",
     "CTH — A change to any heading of Chapter 95 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.95", True),
    ("96", "combined",
     "CTH — A change to any heading of Chapter 96 from any other heading; or RVC ≥ 40% (Build-Down) or 30% (Net Cost).",
     40.0, "build_down", "heading", "rvc_net_cost", 30.0, "net_cost",
     "CPTPP Annex 3-D, Ch.96", True),

    # ─── Section XXI ───────────────────────────────────────────────────────────

    ("97", "tariff_shift",
     "CTH — A change to any heading of Chapter 97 from any other heading.",
     None, None, "heading", None, None, None, "CPTPP Annex 3-D, Ch.97", True),
]

COLUMNS = [
    "hs_code", "rule_type", "rule_text", "value_threshold", "rvc_method",
    "ts_heading_level", "secondary_rule_type", "secondary_value_threshold",
    "secondary_rvc_method", "source_reference", "is_default",
]
