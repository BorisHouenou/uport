"""
CETA Product-Specific Rules of Origin — Annex II to the Protocol on Rules of Origin
Source: Canada-EU Comprehensive Economic and Trade Agreement

CETA uses MaxNOM (Maximum Non-Originating Materials as % of ex-works price).
MaxNOM 45% is equivalent to RVC ≥ 55% Build-Down method.
MaxNOM 50% is equivalent to RVC ≥ 50%.
MaxNOM 40% is equivalent to RVC ≥ 60%.

For the engine, we store the minimum RVC threshold (1 - MaxNOM/100) as value_threshold.
"""

# (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
#  sec_type, sec_threshold, sec_rvc, source_ref, is_default)
CETA_RULES = [

    # ─── Section I — Live Animals; Animal Products ─────────────────────────────

    ("01", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.01", True),
    ("02", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.02", True),
    ("03", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.03", True),
    ("04", "wholly_obtained",
     "Wholly obtained; or manufacture in which all the materials of Chapter 4 used are wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.04", True),
    ("05", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.05", True),

    # ─── Section II — Vegetable Products ──────────────────────────────────────

    ("06", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.06", True),
    ("07", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.07", True),
    ("08", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.08", True),
    ("09", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.09", True),
    ("10", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.10", True),
    ("11", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.11", True),
    ("12", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.12", True),
    ("13", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.13", True),
    ("14", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.14", True),

    # ─── Section III ───────────────────────────────────────────────────────────

    ("15", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.15", True),

    # ─── Section IV — Prepared Foods ──────────────────────────────────────────

    ("16", "tariff_shift",
     "CC — Manufacture from materials of any other chapter. All the materials of Chapters 1 and 3 used must be wholly obtained.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.16", True),
    ("17", "tariff_shift",
     "CC — Manufacture from materials of any other chapter in which all the materials of Chapter 17 used are wholly obtained.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.17", True),
    ("18", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.18", True),
    ("19", "tariff_shift",
     "CC — Manufacture from materials of any other chapter, except from Chapter 11.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.19", True),
    ("20", "tariff_shift",
     "CC — Manufacture from materials of any other chapter, except from Chapter 7 or 8.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.20", True),
    ("21", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.21", True),
    ("22", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.22", True),
    ("23", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.23", True),
    ("24", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.24", True),

    # ─── Section V — Minerals ─────────────────────────────────────────────────

    ("25", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.25", True),
    ("26", "wholly_obtained",
     "Wholly obtained.",
     None, None, None, None, None, None, "CETA Annex II, Ch.26", True),
    ("27", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.27", True),

    # ─── Section VI — Chemicals ────────────────────────────────────────────────

    ("28", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.28", True),
    ("29", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.29", True),

    # Pharmaceuticals (3003/3004) — specific rules
    ("3003", "tariff_shift",
     "CTH — Manufacture from materials of any heading except that of the product, provided: all the materials used are classified in a heading other than that of the product; and the value of all the materials used does not exceed 50% of the ex-works price of the product.",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.30 (3003)", False),
    ("3004", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.30 (3004)", False),
    ("30", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.30", True),

    ("31", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.31", True),
    ("32", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.32", True),
    ("33", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.33", True),
    ("34", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.34", True),
    ("35", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.35", True),
    ("36", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.36", True),
    ("37", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.37", True),
    ("38", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.38", True),

    # ─── Section VII — Plastics & Rubber ──────────────────────────────────────

    ("39", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.39", True),
    ("40", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.40", True),

    # ─── Section VIII — Leather ────────────────────────────────────────────────

    ("41", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.41", True),
    ("42", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.42", True),
    ("43", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.43", True),

    # ─── Section IX — Wood & Paper ─────────────────────────────────────────────

    ("44", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.44", True),
    ("45", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.45", True),
    ("46", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.46", True),
    ("47", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.47", True),
    ("48", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.48", True),
    ("49", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.49", True),

    # ─── Section XI — Textiles ─────────────────────────────────────────────────
    # CETA uses a "two-stage" or "fabric-forward" approach for most textiles.
    # Woven fabrics: CC; Apparel: CTH from fabric OR CC with RVC restriction.

    ("50", "tariff_shift",
     "CC — Manufacture from materials of any other chapter, except from that of headings 50.04 through 50.06.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.50", True),
    ("51", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.51", True),
    ("52", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.52", True),
    ("53", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.53", True),
    ("54", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.54", True),
    ("55", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.55", True),
    ("56", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.56", True),
    ("57", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.57", True),
    ("58", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.58", True),
    ("59", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.59", True),
    ("60", "tariff_shift",
     "CC — Manufacture from materials of any other chapter.",
     None, None, "chapter", None, None, None, "CETA Annex II, Ch.60", True),

    # Apparel — knitted (Ch 61): CTH from fabric stage
    ("61", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or CC accompanied by knitting or crocheting.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.61", True),

    # Apparel — woven (Ch 62): CTH from fabric stage
    ("62", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or CC accompanied by weaving.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.62", True),

    ("63", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.63", True),

    # ─── Section XII — Footwear ────────────────────────────────────────────────

    ("64", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from assembled uppers of heading 64.06.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.64", True),
    ("65", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.65", True),
    ("66", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.66", True),
    ("67", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.67", True),

    # ─── Section XIII — Stone, Ceramics, Glass ────────────────────────────────

    ("68", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.68", True),
    ("69", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.69", True),
    ("70", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.70", True),

    # ─── Section XIV — Precious Metals ────────────────────────────────────────

    ("71", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.71", True),

    # ─── Section XV — Base Metals ─────────────────────────────────────────────

    ("72", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.72", True),
    ("73", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.73", True),
    ("74", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.74", True),
    ("75", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.75", True),
    ("76", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.76", True),
    ("78", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.78", True),
    ("79", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.79", True),
    ("80", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.80", True),
    ("81", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.81", True),
    ("82", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.82", True),
    ("83", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.83", True),

    # ─── Section XVI — Machinery ───────────────────────────────────────────────

    ("84", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.84", True),
    ("85", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.85", True),

    # Telephones (8517) — CTH or MaxNOM 50%
    ("8517", "combined",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW), i.e. RVC ≥ 50%.",
     50.0, "build_down", "heading", "rvc_build_down", 50.0, "build_down",
     "CETA Annex II, Ch.85 (8517)", False),

    # Electronic integrated circuits (8542) — CTH or MaxNOM 50%
    ("8542", "combined",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", "rvc_build_down", 50.0, "build_down",
     "CETA Annex II, Ch.85 (8542)", False),

    # ─── Section XVII — Vehicles ───────────────────────────────────────────────

    ("86", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.86", True),

    # Passenger vehicles (8703) — MaxNOM 45% = RVC ≥ 55%
    ("8703", "rvc_build_down",
     "MaxNOM 45% (EXW) — Non-originating materials must not exceed 45% of the ex-works price of the product. Equivalently, originating content must be at least 55% (RVC Build-Down ≥ 55%).",
     55.0, "build_down", None, None, None, None,
     "CETA Annex II, Ch.87 (8703)", False),

    # Heavy trucks (8704) — MaxNOM 45% = RVC ≥ 55%
    ("8704", "rvc_build_down",
     "MaxNOM 45% (EXW) — Non-originating materials must not exceed 45% of the ex-works price.",
     55.0, "build_down", None, None, None, None,
     "CETA Annex II, Ch.87 (8704)", False),

    # Auto parts (8708) — MaxNOM 45% = RVC ≥ 55%
    ("8708", "rvc_build_down",
     "MaxNOM 45% (EXW) — Non-originating materials must not exceed 45% of the ex-works price.",
     55.0, "build_down", None, None, None, None,
     "CETA Annex II, Ch.87 (8708)", False),

    # Tractors (8701) — MaxNOM 50% = RVC ≥ 50%
    ("8701", "rvc_build_down",
     "MaxNOM 50% (EXW) — Non-originating materials must not exceed 50% of the ex-works price.",
     50.0, "build_down", None, None, None, None,
     "CETA Annex II, Ch.87 (8701)", False),

    # Other vehicles Ch 87 default — MaxNOM 50%
    ("87", "rvc_build_down",
     "MaxNOM 50% (EXW) — Non-originating materials must not exceed 50% of the ex-works price of the product.",
     50.0, "build_down", None, None, None, None,
     "CETA Annex II, Ch.87", True),

    # Aircraft (8802) — CTH or MaxNOM 40%
    ("88", "combined",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 40% (EXW).",
     60.0, "build_down", "heading", "rvc_build_down", 60.0, "build_down",
     "CETA Annex II, Ch.88", True),

    ("89", "combined",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 40% (EXW).",
     60.0, "build_down", "heading", "rvc_build_down", 60.0, "build_down",
     "CETA Annex II, Ch.89", True),

    # ─── Section XVIII — Instruments ──────────────────────────────────────────

    ("90", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.90", True),
    ("91", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.91", True),
    ("92", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.92", True),

    # ─── Section XIX — Arms ────────────────────────────────────────────────────

    ("93", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.93", True),

    # ─── Section XX — Misc Manufactured Articles ──────────────────────────────

    ("94", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.94", True),
    ("95", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.95", True),
    ("96", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product; or MaxNOM 50% (EXW).",
     50.0, "build_down", "heading", None, None, None, "CETA Annex II, Ch.96", True),

    # ─── Section XXI ──────────────────────────────────────────────────────────

    ("97", "tariff_shift",
     "CTH — Manufacture from materials of any heading, except from that of the product.",
     None, None, "heading", None, None, None, "CETA Annex II, Ch.97", True),
]

COLUMNS = [
    "hs_code", "rule_type", "rule_text", "value_threshold", "rvc_method",
    "ts_heading_level", "secondary_rule_type", "secondary_value_threshold",
    "secondary_rvc_method", "source_reference", "is_default",
]
