# OpenAlex Research Papers ETL Pipeline

This repository contains a coursework ETL project built in Python. The pipeline extracts scholarly research paper metadata from the OpenAlex API, transforms nested JSON records into a clean tabular structure, loads the final dataset into SQLite, and validates the loaded data with SQL queries.

## Project Overview

The project focuses on research papers related to **renewable energy**. OpenAlex was used as the source system because it provides rich scholarly metadata, including publication details, citation counts, open-access status, journal/source information, authorship data, and institutional affiliations.

The main technical challenge was transforming nested API responses into an analysis-ready relational table. The final pipeline extracts, transforms, cleans, loads, and validates the data in a modular Python workflow.

## Repository Contents

| File | Description |
|---|---|
| `research_papers_etl.py` | Main Python ETL script |
| `Kartikeya_Abhay_Shaha_ETL_Report.pdf` | Coursework report documenting the project |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files and outputs excluded from version control |
| `outputs/` | Placeholder folder for generated outputs |

## ETL Workflow

The pipeline follows five main stages:

1. **Extract**  
   Retrieves article metadata from the OpenAlex Works API using the search topic `renewable energy`.

2. **Transform**  
   Converts nested JSON records into a flat tabular format. The transformation extracts fields such as title, publication year, citation count, open-access status, journal name, first author, author count, institution count, DOI, and paper URL.

3. **Clean**  
   Standardizes dates and numeric fields, fills missing text values, handles missing open-access flags, removes invalid records, and drops duplicate papers.

4. **Load**  
   Loads the cleaned dataset into a SQLite database table named `research_papers`.

5. **Validate**  
   Runs SQL queries to preview loaded records and generate summary statistics.

## Technologies Used

- Python
- OpenAlex API
- pandas
- requests
- SQLite
- SQL

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/openalex-research-papers-etl.git
cd openalex-research-papers-etl
