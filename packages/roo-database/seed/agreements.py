"""
FTA agreement metadata seed data.

Each entry maps to one row in trade_agreements.
parties = all ISO-3166 alpha-2 country codes that are signatories.
"""

EU_27 = [
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
]

CPTPP_PARTIES = ["AU", "BN", "CA", "CL", "JP", "MX", "MY", "NZ", "PE", "SG", "VN"]

AFCFTA_PARTIES = [
    "DZ", "AO", "BJ", "BW", "BF", "BI", "CM", "CV", "CF", "TD",
    "KM", "CG", "CD", "CI", "DJ", "EG", "GQ", "ER", "SZ", "ET",
    "GA", "GM", "GH", "GN", "GW", "KE", "LS", "LR", "LY", "MG",
    "MW", "ML", "MR", "MU", "MA", "MZ", "NA", "NE", "NG", "RW",
    "ST", "SN", "SL", "SO", "ZA", "SS", "SD", "TZ", "TG", "TN",
    "UG", "ZM", "ZW",
]

AGREEMENTS = [
    {
        "code": "cusma",
        "name": "Canada-United States-Mexico Agreement (CUSMA/USMCA)",
        "parties": ["CA", "US", "MX"],
        "effective_date": "2020-07-01",
        "description": (
            "Successor to NAFTA. Governs trade in goods, services, and investment "
            "among Canada, the United States, and Mexico. Rules of Origin in Chapter 4 "
            "and Annex 4-B."
        ),
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/cusma-aceum/text-texte/toc-tdm.aspx",
    },
    {
        "code": "ceta",
        "name": "Canada-European Union Comprehensive Economic and Trade Agreement (CETA)",
        "parties": ["CA"] + EU_27,
        "effective_date": "2017-09-21",
        "description": (
            "Provisional application since September 2017. Rules of Origin in the Protocol "
            "on Rules of Origin and Origin Procedures and Annex II."
        ),
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/ceta-aecg/index.aspx",
    },
    {
        "code": "cptpp",
        "name": "Comprehensive and Progressive Agreement for Trans-Pacific Partnership (CPTPP)",
        "parties": CPTPP_PARTIES,
        "effective_date": "2018-12-30",
        "description": (
            "11-country agreement across Asia-Pacific. Rules of Origin in Chapter 3 "
            "and Annex 3-D. UK accession in force 2024."
        ),
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/cptpp-ptpgp/index.aspx",
    },
    {
        "code": "afcfta",
        "name": "African Continental Free Trade Area (AfCFTA)",
        "parties": AFCFTA_PARTIES,
        "effective_date": "2021-01-01",
        "description": (
            "55-country continental FTA. Rules of Origin in Annex 2 of the Protocol "
            "on Trade in Goods. Phase 1 (manufacturing) and Phase 2 (services) goods covered."
        ),
        "source_url": "https://au-afcfta.org/",
    },
    {
        "code": "cufta",
        "name": "Canada-Ukraine Free Trade Agreement (CUFTA)",
        "parties": ["CA", "UA"],
        "effective_date": "2017-08-01",
        "description": "Bilateral FTA. Rules of Origin aligned with CETA protocol.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/ukraine/fta-ale/index.aspx",
    },
    {
        "code": "ckfta",
        "name": "Canada-Korea Free Trade Agreement (CKFTA)",
        "parties": ["CA", "KR"],
        "effective_date": "2015-01-01",
        "description": "Bilateral FTA. Rules of Origin in Chapter 3 and Annex 3-A.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/korea-coree/fta-ale/index.aspx",
    },
    {
        "code": "ccofta",
        "name": "Canada-Colombia Free Trade Agreement",
        "parties": ["CA", "CO"],
        "effective_date": "2011-08-15",
        "description": "Bilateral FTA.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/colombia-colombie/index.aspx",
    },
    {
        "code": "cpafta",
        "name": "Canada-Peru Free Trade Agreement",
        "parties": ["CA", "PE"],
        "effective_date": "2009-08-01",
        "description": "Bilateral FTA.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/peru-perou/index.aspx",
    },
    {
        "code": "cifta",
        "name": "Canada-Israel Free Trade Agreement (CIFTA)",
        "parties": ["CA", "IL"],
        "effective_date": "1997-01-01",
        "description": "Bilateral FTA.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/israel/index.aspx",
    },
    {
        "code": "cjfta",
        "name": "Canada-Jordan Free Trade Agreement",
        "parties": ["CA", "JO"],
        "effective_date": "2012-10-01",
        "description": "Bilateral FTA.",
        "source_url": "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/jordan-jordanie/index.aspx",
    },
]
