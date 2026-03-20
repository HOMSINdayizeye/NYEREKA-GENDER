# NYEREKA Gender Data Portal

A Streamlit-based prototype to help CSOs and policy actors discover, interpret, and use gender-related resources with less friction.

## Problem Context

CSOs and policy actors repeatedly struggle to:
- Find up-to-date gender-related data quickly
- Locate the correct institution and latest source
- Work with PDF-heavy or narrative-only resources
- Access disaggregated and district-useful data
- Move fast enough for advocacy and policy cycles

## Project Mission

Build a **Streamlit prototype** that helps users discover, interpret, and use gender-related resources with less friction.

## Getting Started

### Prerequisites
- Python 3.8+
- Streamlit

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd nyereka-gender-app

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

## Project Structure

```
nyereka-gender-app/
├── app.py                      # Main entry point (Nyereka branding + navigation)
├── requirements.txt            # Dependencies (streamlit, pandas, plotly, requests)
├── README.md                   # Project documentation
├── VALIDATION.md               # Data validation rules
├── .gitignore
├── .streamlit/                 # Streamlit configuration (theme, layout)
│   └── config.toml

├── data/
│   └── sample/                 # Sample dataset (for testing/demo)
│       ├── studies.csv
│       ├── study_resources.csv
│       └── quality_report.csv

├── pages/
│   ├── Discovery.py          # 🔎 Smart search & filtering
│   ├── Dashboard.py           # 📊 District insights & visualization
│   ├── Data_Quality.py       # ⚠️ Data quality indicators
│   ├── Advocacy_Assistant.py # 🎯 Advocacy recommendations (KEY FEATURE)
│   └── Reports.py             # 📄 Generate/export insights

└── src/
    ├── __init__.py
    ├── loaders.py               # Load + preprocess data
    ├── filters.py              # Search & filtering logic
    ├── link_checker.py         # Validate dataset/report links
    ├── quality_badges.py       # Data quality indicators
    └── insights.py             # Advocacy insights & recommendations
```

## Key Features

- **Discovery** - Smart search and filtering by category, year, source
- **Dashboard** - District-level insights and visualizations
- **Data Quality** - Quality indicators and caveats for each resource
- **Advocacy Assistant** - Generate recommendations for advocacy (KEY FEATURE)
- **Reports** - Generate and export insights

## Target Users

- Civil Society Organizations (CSOs)
- Policy analysts and researchers
- Advocacy groups
- Government stakeholders
- Development partners

## Data Source

The application uses a baseline CSV inventory containing gender-related resources with the following metadata:
- Resource title
- Institution/Source
- Date/Year
- Geographic coverage
- Data type (PDF, dataset, report)
- Category
- URL/Link
- Quality indicators

## Scope & Constraints

### In Scope
- Use baseline CSV inventory provided for fast start
- Validate key resources directly from NISR links
- Streamlit web application

### Out of Scope
- Bypassing restricted systems or protected endpoints
- Building backend databases (use provided CSV as data source)

## License

This project is for prototyping purposes. Data sources are owned by their respective institutions (primarily NISR - National Institute of Statistics of Rwanda).

## Contributing

Contributions are welcome! Please follow the existing code structure and add appropriate tests for new features.
