"""
Wholly Obtained (WO) / Entirely Obtained rules.

A good is wholly obtained in a country when it is:
  • Mineral products extracted from that country's soil/seabed
  • Plants and plant products grown and harvested there
  • Live animals born and raised there
  • Products from hunting/fishing conducted there
  • Fish/sea products caught by vessels of that country
  • Goods produced from the above exclusively

Reference: CUSMA Article 4.5, CETA Annex II, CPTPP Article 3.2
"""
from __future__ import annotations

from models import WhollyObtainedResult

# Categories recognised as "wholly obtained" under most FTAs
WHOLLY_OBTAINED_CATEGORIES: dict[str, str] = {
    "mineral": "Mineral products extracted or taken from the soil, waters, seabed or subsoil",
    "plant": "Vegetable products grown, picked, harvested, or gathered",
    "animal_born": "Live animals born and raised",
    "animal_product": "Products obtained from live animals (milk, wool, eggs, etc.)",
    "hunt_fish": "Products of hunting, trapping, fishing, aquaculture, gathering, or capturing",
    "sea_product": "Fish and other marine products taken from the sea or seabed",
    "waste": "Waste and scrap derived from production operations — fit only for recovery of raw materials",
    "recycled": "Recovered goods derived entirely from used articles in that country",
}


def check_wholly_obtained(
    production_country: str,
    category: str | None,
    agreement_code: str = "generic",
) -> WhollyObtainedResult:
    """
    Determine if a product qualifies as Wholly Obtained.

    Args:
        production_country: ISO-3166 alpha-2 of the production country
        category: one of the keys in WHOLLY_OBTAINED_CATEGORIES, or None
        agreement_code: the FTA being evaluated (affects some edge cases)
    """
    if category is None:
        return WhollyObtainedResult(
            passes=False,
            category=None,
            production_country=production_country,
            detail=(
                "Cannot determine Wholly Obtained status: product category not specified. "
                "A BOM-based analysis (RVC or Tariff Shift) is required."
            ),
        )

    if category not in WHOLLY_OBTAINED_CATEGORIES:
        return WhollyObtainedResult(
            passes=False,
            category=category,
            production_country=production_country,
            detail=(
                f"Category '{category}' is not a recognised Wholly Obtained category. "
                f"Valid categories: {', '.join(WHOLLY_OBTAINED_CATEGORIES.keys())}"
            ),
        )

    description = WHOLLY_OBTAINED_CATEGORIES[category]
    return WhollyObtainedResult(
        passes=True,
        category=category,
        production_country=production_country,
        detail=(
            f"PASS — Wholly Obtained under '{agreement_code}'. "
            f"Category: {description}. "
            f"Production country: {production_country}."
        ),
    )


def is_wholly_obtained_hs(hs_code: str) -> bool:
    """
    Heuristic: certain HS chapters are almost always Wholly Obtained.
    Used to pre-screen before running a full BOM analysis.
    """
    chapter = int(hs_code[:2])
    # Chapters 1-24 (animals, plants, food), 25-27 (minerals, fuels), 47-49 (paper pulp from forest)
    return chapter in set(range(1, 28)) or chapter in {47, 26, 27}
