# Data Validation Rules

This document outlines the validation rules applied to ensure data quality and reliability.

## Resource Validation Rules

### 1. Link Validation
- All external URLs must be validated for accessibility
- NISR links must point to official government domains
- Broken links must be flagged with a warning badge

### 2. Metadata Requirements
Each resource must include:
- Title (required)
- Source/Institution (required)
- Year/Date (required, must be >= 2015)
- Category (required: Health, Education, Employment, Violence, Leadership, Other)
- Geographic coverage (required: National, Province, District)
- Data type (required: PDF, Dataset, API, Report)

### 3. Data Quality Indicators

#### Quality Badges
- **High Quality**: Official government source, recent data (within 2 years), comprehensive coverage
- **Medium Quality**: NGO/research source, data within 5 years, partial coverage
- **Limited**: Older data, narrow scope, or incomplete documentation

#### Caveat Flags
- Disaggregation limitations
- Geographic gaps
- Temporal inconsistencies
- Methodology concerns

### 4. Provenance Verification
- All NISR resources must be validated against official NISR portal
- Third-party sources must include citation information
- Data derived from other sources must be documented

## Validation Process

1. **Automatic Checks**
   - URL accessibility testing
   - Required field validation
   - Date format standardization
   - Category classification

2. **Manual Review**
   - Source verification
   - Quality assessment
   - Relevance scoring

## Quality Score Calculation

```
Quality Score = (Freshness × 0.3) + (Source Authority × 0.3) + (Coverage × 0.2) + (Documentation × 0.2)
```

- Freshness: 0-100 based on data age
- Source Authority: 0-100 based on institution credibility
- Coverage: 0-100 based on geographic/disaggregation completeness
- Documentation: 0-100 based on metadata quality
