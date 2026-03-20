
========================================
## Team information
========================================
- Team name: NYEREKA GENDER
- Team members: 
1. Amos NDAYIZEYE           
2. Amos MUSABYIMANA     
3. Abraham TUYISHIME    
========================================
- Contact:
========================================
1. homsindayizeye@gmail.com
2. musabiano@gmail.com
3. tuyishimeabraham455@gmail.com
========================================
## Problem
========================================
Users struggle to find up-to-date gender data, interpret PDF-heavy reports, access district-level insights, and use data efficiently for advocacy.and get accessible information related to gender.
========================================
## user
========================================
- Target user persona:
Government gender and planning officers MINISTRY in charge  of gender, Civil society and NGOs working on gender (women’s rights organizations, advocacy coalitions, international NGOs), Researchers, consultants, and students who want an easier entry point to gender‑related indicators
Community
==============================================
- Advocacy scenario:
=============================================
A women’s rights NGO in Huye uses  to show that girls’ lower‑secondary completion is far below boys and the national average.
​The tool quickly pulls DHS‑based indicators and visualizes the gap by sex and district.
NYEREKA Gender then generates a brief recommending bursaries and mentorship programs to close the gap.
Armed with this evidence, the NGO secures a commitment from district leaders to increase the education budget for vulnerable girls.
===============================================
## Solution summary
===============================================
- a Streamlit-based application designed to help users quickly discover, understand, and use gender-related data for advocacy and policy decision-making.

- Why this approach?
- Core user flow:
===============================================
## Technical setup
================================================
- Streamlit entry point: app.py
- Install command: pip install -r requirements.txt
- Run command: streamlit run app.py

## Data and provenance
- Files used: resources.csv (baseline CSV inventory)
- Direct NISR resources validated: NISR statistical yearbooks, DHS data portal
- Provenance notes: All data sourced from publicly available NISR publications and validated government portals

## Demo evidence
- Query/scenario 1: Search for education indicators by district and gender
- Query/scenario 2: Filter resources by year and category (health, education, employment)
- Policy insight produced: District-level gender gap analysis for secondary education completion rates

## Limitations and next steps
- Known data gaps: Limited real-time data, some PDF-only resources
- Technical gaps: No backend database, relies on static CSV
- Improvement roadmap: Add live API connections, implement data validation, expand to mobile-friendly version
