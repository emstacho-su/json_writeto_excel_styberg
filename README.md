# ISO 9001:2015 Audit JSON to Excel Uploader

This Flask-based web app allows users to paste or upload JSON data from ISO audit reviews, and automatically append the results to an Excel workbook.

### Features
- Accepts structured JSON input for clauses
- Appends to four Excel sheets:
  - Null Hypothesis
  - Material Evidence
  - Gap Severity
  - Longitudinal Tracking

### Requirements
- Flask
- pandas
- openpyxl

### Deployment
This app is configured to deploy automatically via [Render.com](https://render.com) using `render.yaml`.

### Usage
1. Paste JSON into the form on the homepage.
2. Click submit.
3. Excel file is updated on the backend.

> Note: `audit_data.xlsx` must be present in the root directory for the script to function properly.
