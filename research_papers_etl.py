import os
import sqlite3
import requests
import pandas as pd

API_URL = "https://api.openalex.org/works"
DB_NAME = "research_papers_etl.db"
TABLE_NAME = "research_papers"

SEARCH_TOPIC = "renewable energy"
START_YEAR = 2024
END_YEAR = 2026
PER_PAGE = 50


OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")


def extract_papers():
  
    params = {
        "search": SEARCH_TOPIC,
        "filter": f"publication_year:{START_YEAR}-{END_YEAR},type:article",
        "per_page": PER_PAGE
    }

    
    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def transform_to_dataframe(data):
    
    results = data.get("results", [])
    rows = []

    for work in results:
        authorships = work.get("authorships", [])
        open_access = work.get("open_access", {})
        primary_location = work.get("primary_location", {}) or {}
        source = primary_location.get("source", {}) or {}

        # First author name
        first_author = None
        if authorships:
            first_author = authorships[0].get("author", {}).get("display_name")

        # Count unique institutions appearing across authorships
        institution_ids = set()
        for authorship in authorships:
            institutions = authorship.get("institutions", [])
            for institution in institutions:
                inst_id = institution.get("id")
                if inst_id:
                    institution_ids.add(inst_id)

        row = {
            "paper_id": work.get("id"),
            "title": work.get("display_name"),
            "publication_year": work.get("publication_year"),
            "publication_date": work.get("publication_date"),
            "cited_by_count": work.get("cited_by_count"),
            "is_open_access": open_access.get("is_oa"),
            "oa_status": open_access.get("oa_status"),
            "journal_name": source.get("display_name"),
            "first_author": first_author,
            "author_count": len(authorships),
            "institutions_count": len(institution_ids),
            "language": work.get("language"),
            "doi": work.get("doi"),
            "paper_url": work.get("primary_location", {}).get("landing_page_url"),
            "search_topic": SEARCH_TOPIC
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def clean_papers_data(df):
   
    if df.empty:
        return df


    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")

    numeric_cols = ["publication_year", "cited_by_count", "author_count", "institutions_count"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")


    df["is_open_access"] = df["is_open_access"].fillna(False)


    text_cols = ["title", "oa_status", "journal_name", "first_author", "language", "doi", "paper_url"]
    for col in text_cols:
        df[col] = df[col].fillna("Unknown")


    df = df.dropna(subset=["paper_id", "publication_year"])

   
    df = df.drop_duplicates(subset=["paper_id"]).reset_index(drop=True)

    return df


def load_to_sqlite(df, db_name=DB_NAME, table_name=TABLE_NAME):
  
    connection = sqlite3.connect(db_name)
    df.to_sql(table_name, connection, if_exists="replace", index=False)
    connection.close()


def read_from_sqlite(db_name=DB_NAME, table_name=TABLE_NAME):
   
    connection = sqlite3.connect(db_name)
    query = f"SELECT * FROM {table_name} LIMIT 10;"
    df_preview = pd.read_sql_query(query, connection)
    connection.close()
    return df_preview


def get_sql_summary(db_name=DB_NAME, table_name=TABLE_NAME):

    connection = sqlite3.connect(db_name)

    summary_query = f"""
    SELECT
        COUNT(*) AS total_papers,
        MIN(publication_year) AS earliest_year,
        MAX(publication_year) AS latest_year,
        AVG(cited_by_count) AS avg_citations,
        SUM(CASE WHEN is_open_access = 1 THEN 1 ELSE 0 END) AS open_access_papers
    FROM {table_name};
    """

    papers_per_year_query = f"""
    SELECT publication_year, COUNT(*) AS papers_count
    FROM {table_name}
    GROUP BY publication_year
    ORDER BY publication_year;
    """

    top_cited_query = f"""
    SELECT title, cited_by_count, journal_name
    FROM {table_name}
    ORDER BY cited_by_count DESC
    LIMIT 5;
    """

    summary_df = pd.read_sql_query(summary_query, connection)
    papers_per_year_df = pd.read_sql_query(papers_per_year_query, connection)
    top_cited_df = pd.read_sql_query(top_cited_query, connection)

    connection.close()

    return summary_df, papers_per_year_df, top_cited_df


def main():
    """
    Run the ETL pipeline:
    Extract -> Transform -> Clean -> Load -> Validate
    """
    try:
        print("Starting Research Papers ETL pipeline...")

        raw_data = extract_papers()
        print("Extraction completed successfully.")

        df = transform_to_dataframe(raw_data)
        print(f"Raw rows extracted: {len(df)}")

        cleaned_df = clean_papers_data(df)
        print(f"Cleaned rows ready for loading: {len(cleaned_df)}")
        print("Transformation and cleaning completed successfully.")

        load_to_sqlite(cleaned_df)
        print(f"Data loaded successfully into '{DB_NAME}' (table: '{TABLE_NAME}').")

        preview_df = read_from_sqlite()
        print("\nPreview of data read from SQLite:")
        print(preview_df)

        summary_df, papers_per_year_df, top_cited_df = get_sql_summary()

        print("\nSQL validation summary:")
        print(summary_df)

        print("\nPapers per year:")
        print(papers_per_year_df)

        print("\nTop 5 most cited papers:")
        print(top_cited_df)

        print("\nETL pipeline completed successfully.")

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    except KeyError as e:
        print(f"Missing expected key in API response: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()