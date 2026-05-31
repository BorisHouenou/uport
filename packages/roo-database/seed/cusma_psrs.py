"""
CUSMA/USMCA Product-Specific Rules of Origin — Annex 4-B
Source: Canada-United States-Mexico Agreement, as amended.

Format per rule:
  (hs_code, rule_type, rule_text, value_threshold, rvc_method, ts_level, secondary_type,
   secondary_threshold, secondary_rvc_method, source_ref, is_default)

hs_code can be:
  "XX"    → 2-digit chapter default (is_default=True, covers all unspecified headings)
  "XXXX"  → 4-digit heading override
  "XXXXXX"→ 6-digit subheading override

rule_type values: wholly_obtained, tariff_shift, rvc_build_down, rvc_build_up,
                  rvc_net_cost, combined
"""

# (hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
#  sec_type, sec_threshold, sec_rvc, source_ref, is_default)
CUSMA_RULES = [

    # ─── Section I — Live Animals; Animal Products ─────────────────────────────

    # Ch 01 — Live animals: wholly obtained
    ("01", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.01", True),

    # Ch 02 — Meat: wholly obtained
    ("02", "wholly_obtained",
     "A change to a heading of Chapter 2 from any other chapter; or wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.02", True),

    # Ch 03 — Fish: wholly obtained
    ("03", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.03", True),

    # Ch 04 — Dairy: wholly obtained or CTH
    ("04", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties; or a change to a heading of Chapter 4 from any other chapter.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.04", True),

    # Ch 05 — Animal products: CTH
    ("05", "tariff_shift",
     "A change to a heading of Chapter 5 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.05", True),

    # ─── Section II — Vegetable Products ──────────────────────────────────────

    # Ch 06-14 — Plants and plant products: wholly obtained
    ("06", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.06", True),
    ("07", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.07", True),
    ("08", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.08", True),
    ("09", "tariff_shift",
     "A change to a heading of Chapter 9 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.09", True),
    ("10", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.10", True),
    ("11", "tariff_shift",
     "A change to a heading of Chapter 11 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.11", True),
    ("12", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.12", True),
    ("13", "tariff_shift",
     "A change to a heading of Chapter 13 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.13", True),
    ("14", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.14", True),

    # ─── Section III — Fats & Oils ─────────────────────────────────────────────

    ("15", "tariff_shift",
     "A change to a heading of Chapter 15 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.15", True),

    # ─── Section IV — Prepared Foods ──────────────────────────────────────────

    ("16", "tariff_shift",
     "A change to a heading of Chapter 16 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.16", True),
    ("17", "tariff_shift",
     "A change to a heading of Chapter 17 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.17", True),
    ("18", "tariff_shift",
     "A change to a heading of Chapter 18 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.18", True),
    ("19", "tariff_shift",
     "A change to a heading of Chapter 19 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.19", True),
    ("20", "tariff_shift",
     "A change to a heading of Chapter 20 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.20", True),
    ("21", "tariff_shift",
     "A change to a heading of Chapter 21 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.21", True),
    ("22", "tariff_shift",
     "A change to a heading of Chapter 22 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.22", True),
    ("23", "tariff_shift",
     "A change to a heading of Chapter 23 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.23", True),
    ("24", "tariff_shift",
     "A change to a heading of Chapter 24 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.24", True),

    # ─── Section V — Mineral Products ─────────────────────────────────────────

    ("25", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.25", True),
    ("26", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.26", True),
    ("27", "tariff_shift",
     "A change to a heading of Chapter 27 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.27", True),
    # Crude oil (2709) — wholly obtained
    ("2709", "wholly_obtained",
     "Wholly obtained or produced entirely in the territory of one or more of the Parties.",
     None, None, None, None, None, None, "CUSMA Annex 4-B, Ch.27 (2709)", False),

    # ─── Section VI — Chemicals ────────────────────────────────────────────────

    # Default for most chemical chapters: CTH
    ("28", "tariff_shift",
     "A change to a heading of Chapter 28 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.28", True),
    ("29", "tariff_shift",
     "A change to a heading of Chapter 29 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.29", True),
    ("30", "tariff_shift",
     "A change to a heading of Chapter 30 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.30", True),
    ("31", "tariff_shift",
     "A change to a heading of Chapter 31 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.31", True),
    ("32", "tariff_shift",
     "A change to a heading of Chapter 32 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.32", True),
    ("33", "tariff_shift",
     "A change to a heading of Chapter 33 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.33", True),
    ("34", "tariff_shift",
     "A change to a heading of Chapter 34 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.34", True),
    ("35", "tariff_shift",
     "A change to a heading of Chapter 35 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.35", True),
    ("36", "tariff_shift",
     "A change to a heading of Chapter 36 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.36", True),
    ("37", "tariff_shift",
     "A change to a heading of Chapter 37 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.37", True),
    ("38", "tariff_shift",
     "A change to a heading of Chapter 38 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.38", True),

    # Pharmaceuticals (3004) — RVC or CTH
    ("3004", "combined",
     "A change to heading 30.04 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.30 (3004)", False),

    # ─── Section VII — Plastics & Rubber ──────────────────────────────────────

    ("39", "tariff_shift",
     "A change to a heading of Chapter 39 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.39", True),
    ("40", "tariff_shift",
     "A change to a heading of Chapter 40 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.40", True),

    # Pneumatic tyres (4011) — CTH or RVC-40%
    ("4011", "combined",
     "A change to heading 40.11 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.40 (4011)", False),

    # ─── Section VIII — Leather ────────────────────────────────────────────────

    ("41", "tariff_shift",
     "A change to a heading of Chapter 41 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.41", True),
    ("42", "tariff_shift",
     "A change to a heading of Chapter 42 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.42", True),
    ("43", "tariff_shift",
     "A change to a heading of Chapter 43 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.43", True),

    # ─── Section IX — Wood & Paper ─────────────────────────────────────────────

    ("44", "tariff_shift",
     "A change to a heading of Chapter 44 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.44", True),
    ("45", "tariff_shift",
     "A change to a heading of Chapter 45 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.45", True),
    ("46", "tariff_shift",
     "A change to a heading of Chapter 46 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.46", True),
    ("47", "tariff_shift",
     "A change to a heading of Chapter 47 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.47", True),
    ("48", "tariff_shift",
     "A change to a heading of Chapter 48 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.48", True),
    ("49", "tariff_shift",
     "A change to a heading of Chapter 49 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.49", True),

    # ─── Section XI — Textiles ─────────────────────────────────────────────────
    # Yarn-forward rule: the good must be made entirely from yarn (or earlier stage)
    # produced in the CUSMA region — CC (Change in Chapter) unless otherwise noted.

    ("50", "tariff_shift",
     "CC — A change to a heading of Chapter 50 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.50", True),
    ("51", "tariff_shift",
     "CC — A change to a heading of Chapter 51 from any other chapter, except from headings 51.06 through 51.13.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.51", True),
    ("52", "tariff_shift",
     "CC — A change to a heading of Chapter 52 from any other chapter, except from headings 52.04 through 52.12.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.52", True),
    ("53", "tariff_shift",
     "CC — A change to a heading of Chapter 53 from any other chapter, except from headings 53.07 through 53.08 or 53.10 through 53.11.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.53", True),
    ("54", "tariff_shift",
     "CC — A change to a heading of Chapter 54 from any other chapter, except from heading 54.02 through 54.05.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.54", True),
    ("55", "tariff_shift",
     "CC — A change to a heading of Chapter 55 from any other chapter, except from headings 55.01 through 55.07.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.55", True),
    ("56", "tariff_shift",
     "CC — A change to a heading of Chapter 56 from any other chapter, except from headings 54.02, 54.03, 54.04, 55.01 through 55.07 or 55.09 through 55.10.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.56", True),
    ("57", "tariff_shift",
     "CC — A change to a heading of Chapter 57 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.57", True),
    ("58", "tariff_shift",
     "CC — A change to a heading of Chapter 58 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.58", True),
    ("59", "tariff_shift",
     "CC — A change to a heading of Chapter 59 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12, 54.02 through 54.05.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.59", True),
    ("60", "tariff_shift",
     "CC — A change to a heading of Chapter 60 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.60", True),
    # Apparel Ch 61/62 — yarn-forward (CC)
    ("61", "tariff_shift",
     "CC — A change to a heading of Chapter 61 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12, 53.07, 53.08, 53.10, 53.11, 54.02 through 54.06, 55.04 through 55.10, 55.11, 58.01, 58.02.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.61", True),
    ("62", "tariff_shift",
     "CC — A change to a heading of Chapter 62 from any other chapter, except from headings 51.06 through 51.13, 52.04 through 52.12, 53.07, 53.08, 53.10, 53.11, 54.02 through 54.06, 55.04 through 55.10, 55.11, 58.01, 58.02.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.62", True),
    ("63", "tariff_shift",
     "CC — A change to a heading of Chapter 63 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.63", True),

    # ─── Section XII — Footwear ────────────────────────────────────────────────

    ("64", "tariff_shift",
     "A change to a heading of Chapter 64 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.64", True),
    ("65", "tariff_shift",
     "A change to a heading of Chapter 65 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.65", True),
    ("66", "tariff_shift",
     "A change to a heading of Chapter 66 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.66", True),
    ("67", "tariff_shift",
     "A change to a heading of Chapter 67 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.67", True),

    # ─── Section XIII — Stone, Ceramics, Glass ────────────────────────────────

    ("68", "tariff_shift",
     "A change to a heading of Chapter 68 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.68", True),
    ("69", "tariff_shift",
     "A change to a heading of Chapter 69 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.69", True),
    ("70", "tariff_shift",
     "A change to a heading of Chapter 70 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.70", True),

    # ─── Section XIV — Precious Metals ────────────────────────────────────────

    ("71", "tariff_shift",
     "A change to a heading of Chapter 71 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.71", True),

    # ─── Section XV — Base Metals ─────────────────────────────────────────────

    ("72", "tariff_shift",
     "A change to a heading of Chapter 72 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.72", True),
    ("73", "tariff_shift",
     "A change to a heading of Chapter 73 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.73", True),
    ("74", "tariff_shift",
     "A change to a heading of Chapter 74 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.74", True),
    ("75", "tariff_shift",
     "A change to a heading of Chapter 75 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.75", True),
    ("76", "tariff_shift",
     "A change to a heading of Chapter 76 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.76", True),
    ("78", "tariff_shift",
     "A change to a heading of Chapter 78 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.78", True),
    ("79", "tariff_shift",
     "A change to a heading of Chapter 79 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.79", True),
    ("80", "tariff_shift",
     "A change to a heading of Chapter 80 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.80", True),
    ("81", "tariff_shift",
     "A change to a heading of Chapter 81 from any other chapter.",
     None, None, "chapter", None, None, None, "CUSMA Annex 4-B, Ch.81", True),
    ("82", "tariff_shift",
     "A change to a heading of Chapter 82 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.82", True),
    ("83", "tariff_shift",
     "A change to a heading of Chapter 83 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.83", True),

    # ─── Section XVI — Machinery ───────────────────────────────────────────────

    # Default for machinery chapters: CTH
    ("84", "tariff_shift",
     "A change to a heading of Chapter 84 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.84", True),
    ("85", "tariff_shift",
     "A change to a heading of Chapter 85 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.85", True),

    # Computers (8471) — CTH
    ("8471", "tariff_shift",
     "CTH — A change to heading 84.71 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.84 (8471)", False),

    # Semiconductor mfg equipment (8486) — CTH or RVC-40%
    ("8486", "combined",
     "A change to heading 84.86 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.84 (8486)", False),

    # Telephones / smartphones (8517) — RVC-40%
    ("8517", "rvc_build_down",
     "No change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method) or 30 percent (Net Cost method).",
     40.0, "build_down", None, "rvc_net_cost", 30.0, "net_cost",
     "CUSMA Annex 4-B, Ch.85 (8517)", False),

    # Electric accumulators / batteries (8507) — CTH or RVC-40%
    ("8507", "combined",
     "A change to heading 85.07 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.85 (8507)", False),

    # Electronic integrated circuits (8542) — CTH or RVC-40%
    ("8542", "combined",
     "A change to heading 85.42 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.85 (8542)", False),

    # Insulated wire & cable (8544) — CTH or RVC-40%
    ("8544", "combined",
     "A change to heading 85.44 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.85 (8544)", False),

    # ─── Section XVII — Vehicles ───────────────────────────────────────────────

    # Default for Section XVII: CTH
    ("86", "tariff_shift",
     "A change to a heading of Chapter 86 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.86", True),

    # Tractors (8701) — RVC-60% (BD) or 50% (NC)
    ("8701", "rvc_build_down",
     "No change in tariff classification required, provided there is a regional value content of not less than 60 percent (Build-Down method) or 50 percent (Net Cost method).",
     60.0, "build_down", None, "rvc_net_cost", 50.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8701)", False),

    # Buses/coaches (8702) — RVC-60% (BD) or 50% (NC)
    ("8702", "rvc_build_down",
     "No change in tariff classification required, provided there is a regional value content of not less than 60 percent (Build-Down method) or 50 percent (Net Cost method).",
     60.0, "build_down", None, "rvc_net_cost", 50.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8702)", False),

    # Passenger vehicles (8703) — RVC-75% (BD) or 65% (NC) — CUSMA Automotive
    ("8703", "rvc_build_down",
     "A change to heading 87.03 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than: (a) 75 percent where the transaction value method is used; or (b) 65 percent where the net cost method is used. NOTE: CUSMA Annex 4-B uses 75/65 as of July 1, 2023.",
     75.0, "build_down", None, "rvc_net_cost", 65.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8703)", False),

    # Light trucks / cargo vehicles (8704) — RVC-60% (BD) or 50% (NC)
    ("8704", "rvc_build_down",
     "No change in tariff classification required, provided there is a regional value content of not less than 60 percent (Build-Down method) or 50 percent (Net Cost method).",
     60.0, "build_down", None, "rvc_net_cost", 50.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8704)", False),

    # Special purpose vehicles (8705) — CTH or RVC-60%
    ("8705", "combined",
     "A change to heading 87.05 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 60 percent (Build-Down method) or 50 percent (Net Cost method).",
     60.0, "build_down", "heading", "rvc_net_cost", 50.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8705)", False),

    # Auto parts (8708) — RVC-65% (BD) or 60% (NC) for listed core parts, else 40% BD
    ("8708", "rvc_build_down",
     "No change in tariff classification required, provided there is a regional value content of not less than 65 percent (Build-Down method) or 60 percent (Net Cost method) for core parts (engines, transmissions, body stampings); or not less than 40 percent (Build-Down method) for other parts of heading 87.08.",
     65.0, "build_down", None, "rvc_net_cost", 60.0, "net_cost",
     "CUSMA Annex 4-B, Ch.87 (8708)", False),

    # Motorcycles (8711) — CTH or RVC-40%
    ("8711", "combined",
     "A change to heading 87.11 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.87 (8711)", False),

    # Bicycles (8712) — CTH
    ("8712", "tariff_shift",
     "CTH — A change to heading 87.12 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.87 (8712)", False),

    # Aircraft (8802) — CTH or RVC-40%
    ("88", "combined",
     "A change to a heading of Chapter 88 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.88", True),

    # Ships (89) — CTH or RVC-40%
    ("89", "combined",
     "A change to a heading of Chapter 89 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.89", True),

    # ─── Section XVIII — Instruments ──────────────────────────────────────────

    ("90", "tariff_shift",
     "A change to a heading of Chapter 90 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.90", True),

    # Medical devices (9018-9021) — CTH or RVC-40%
    ("9018", "combined",
     "A change to heading 90.18 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.90 (9018)", False),
    ("9019", "combined",
     "A change to heading 90.19 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.90 (9019)", False),
    ("9021", "combined",
     "A change to heading 90.21 from any other heading; or no change in tariff classification required, provided there is a regional value content of not less than 40 percent (Build-Down method).",
     40.0, "build_down", "heading", "rvc_build_down", 40.0, "build_down",
     "CUSMA Annex 4-B, Ch.90 (9021)", False),

    ("91", "tariff_shift",
     "A change to a heading of Chapter 91 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.91", True),
    ("92", "tariff_shift",
     "A change to a heading of Chapter 92 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.92", True),

    # ─── Section XIX — Arms ────────────────────────────────────────────────────

    ("93", "tariff_shift",
     "A change to a heading of Chapter 93 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.93", True),

    # ─── Section XX — Misc Manufactured Articles ──────────────────────────────

    ("94", "tariff_shift",
     "A change to a heading of Chapter 94 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.94", True),
    ("95", "tariff_shift",
     "A change to a heading of Chapter 95 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.95", True),
    ("96", "tariff_shift",
     "A change to a heading of Chapter 96 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.96", True),

    # ─── Section XXI ──────────────────────────────────────────────────────────

    ("97", "tariff_shift",
     "A change to a heading of Chapter 97 from any other heading.",
     None, None, "heading", None, None, None, "CUSMA Annex 4-B, Ch.97", True),
]

# Columns: hs_code, rule_type, rule_text, threshold, rvc_method, ts_level,
#          sec_type, sec_threshold, sec_rvc, source_ref, is_default
COLUMNS = [
    "hs_code", "rule_type", "rule_text", "value_threshold", "rvc_method",
    "ts_heading_level", "secondary_rule_type", "secondary_value_threshold",
    "secondary_rvc_method", "source_reference", "is_default",
]
