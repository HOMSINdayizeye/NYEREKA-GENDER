# NYEREKA Gender Data Portal

>  **Status: Prototype / Work in Progress** — Built during a Hackathon

A Streamlit-based prototype to help CSOs and policy actors in **Rwanda** discover, interpret, and use gender-related resources with less friction.

---

## Problem Context

CSOs and policy actors repeatedly struggle to:

- Find up-to-date gender-related data quickly
- Locate the correct institution and latest source
- Work with PDF-heavy or narrative-only resources
- Access disaggregated and district-useful data
- Move fast enough for advocacy and policy cycles

---

## Project Mission

Build a **Streamlit prototype** that helps users discover, interpret, and use gender-related resources with less friction — focused on Rwanda's district-level gender data.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Streamlit

### Installation

```bash
# Clone the repository
git clone https://github.com/HOMSINdayizeye/NYEREKA-GENDER.git
cd nyereka-gender-app

# Install dependencies
pip install -r requirements.txt

# Build processed indicators from raw data in ../data
python scripts/build_indicators.py
```

### Running the Application

```bash
streamlit run app.py
```

If raw files change, rebuild indicators:

```bash
python scripts/build_indicators.py
```

---

## Project Structure

```
nyereka-gender-app/
├── app.py                      # Main entry point (hero + navigation)
├── requirements.txt            # Dependencies (streamlit, pandas, plotly, requests)
├── README.md                   # Project documentation
├── VALIDATION.md               # Data validation rules
├── scripts/
│   └── build_indicators.py     # Build processed indicator tables from raw data
├── .gitignore
├── .streamlit/                 # Streamlit configuration (theme, layout)
│   └── config.toml
├── data/
│   └── processed/              # Generated indicator data used by dashboard
│       ├── indicators.csv
│       ├── indicator_catalog.csv
│       ├── sources.csv
│       ├── quality_summary.csv
│       └── districts.csv
├── pages/
│   ├── Discovery.py           # Smart search/filter + recommendations
│   ├── Dashboard.py           # District-level interactive visualization
│   ├── Data_Quality.py        # Quality scores, caveats, and checklist
│   ├── Advocacy_Assistant.py  # Recommendations + follow-up tracking
│   └── Reports.py             # Quarterly report generation + exports
└── src/
    ├── __init__.py
    ├── loaders.py              # Load + preprocess data
    ├── filters.py              # Search & filtering logic
    ├── link_checker.py         # Validate dataset/report links
    ├── quality_badges.py       # Data quality indicators
    └── insights.py             # Advocacy insights & recommendations
```

---

## Key Features
|--------------------------------------------------------|
| Feature                                  | Status      |
|------------------------------------------|-------------|
|  Discovery / Smart Search                | Working     |
| Dashboard — District-level visualizations| Working     |
|  Data Quality — Quality scores & caveats | Working     |
|  Advocacy Assistant — Recommendations    | Working     |

---

## Target Users

- Civil Society Organizations (CSOs)
- Policy analysts and researchers
- Advocacy groups
- Government stakeholders
- Development partners

---

## Data Sources

The application uses a baseline CSV inventory containing gender-related resources from Rwanda, primarily sourced from:

- **NISR** — National Institute of Statistics of Rwanda
- DHS (Demographic and Health Survey 2019–2020)
- Rwanda Labour Force Survey 2024
- FinScope Rwanda 2024
- PHC5 Public Microdata

---

## Scope & Constraints

### In Scope
- Use baseline CSV inventory provided for fast start
- Validate key resources directly from NISR links
- Streamlit web application focused on Rwanda

### Out of Scope
- Bypassing restricted systems or protected endpoints
- Building backend databases (use provided CSV as data source)

---

## Team
----------------------------------------------------------------------
| Name              |    Role        |                    Email      |
|----------------   |----------------|-------------------------------|
| Amos NDAYIZEYE    |      Developer | homsindayizeye@gmail.com      |
| Amos MUSABYIMANA  | Data Analyst   | musabiano@gmail.com           |
| Abraham TUYISHIME |Developer       | tuyishimeabraham455@gmail.com |
|--------------------------------------------------------------------|

## Contact

For questions or collaboration, reach out to the team:
-  homsindayizeye@gmail.com
-  musabiano@gmail.com
-  tuyishimeabraham455@gmail.com

---

## License

This project was built during a Hackathon for prototyping purposes. Data sources are owned by their respective institutions (primarily NISR — National Institute of Statistics of Rwanda). Not intended for commercial use.
