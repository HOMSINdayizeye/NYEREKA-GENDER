# NYEREKA Gender Data Portal

A Streamlit-based prototype to help CSOs and policy actors discover, interpret, and use gender-related resources with less friction.

## Problem Context

CSOs and policy actors repeatedly struggle to:
- Find up-to-date gender-related data quickly
- Locate the correct institution and latest source
- Work with PDF-heavy or narrative-only resources
- Access disaggregated and district-useful data
- Move fast enough for advocacy and policy cycles

This challenge was selected from workshop and survey evidence because it has the highest urgency and immediate value for evidence-based advocacy.

## Project Mission

Build a **Streamlit prototype** that helps users discover, interpret, and use gender-related resources with less friction.

### Solution Types

The solution may be:
- A dashboard
- A searchable catalog
- A hybrid dashboard + discovery tool

## What Good Looks Like

Your app should help users:

1. **Find relevant resources quickly** - Efficient search and filtering capabilities
2. **Understand resource relevance from metadata** - Clear metadata display showing source, date, coverage
3. **Access source links clearly** - Direct links to original sources (NISR, government portals)
4. **See quality caveats and limitations** - Transparent data quality indicators
5. **Use outputs in one advocacy scenario** - Practical tools for real-world advocacy work

## Scope & Constraints

### In Scope
- Use baseline CSV inventory provided for fast start
- Validate key resources directly from NISR links
- Streamlit web application

### Out of Scope
- Bypassing restricted systems or protected endpoints
- Building backend databases (use provided CSV as data source)

## Getting Started

### Prerequisites
- Python 3.8+
- Streamlit

### Installation

```bash
# Clone the repository
git clone <https://github.com/HOMSINdayizeye/NYEREKA-GENDER.git>
cd NYEREKA-GENDER

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

## Project Structure

```
NYEREKA-GENDER/
├── app.py                 # Main Streamlit application
├── data/
│   └── resources.csv      # Baseline CSV inventory
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

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

## Key Features

- **Searchable Catalog**: Filter resources by category, year, source, and type
- **Dashboard View**: Overview statistics and visualizations
- **Metadata Display**: Clear information about each resource
- **Quality Indicators**: Caveats and limitations clearly shown
- **Direct Links**: Quick access to original NISR sources

## Target Users

- Civil Society Organizations (CSOs)
- Policy analysts and researchers
- Advocacy groups
- Government stakeholders
- Development partners

## License

This project is for prototyping purposes. Data sources are owned by their respective institutions (primarily NISR - National Institute of Statistics of Rwanda).


