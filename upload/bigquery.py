import logging
import argparse
from google.cloud import bigquery


def upload_element_summary_from_gcs_to_bigquery(
        project_id: str,
        dataset_id: str,
        bucket_name: str,
        source_folder: str = 'element_summary',
        table_id: str = 'element_summary_history'
        ):

    client = bigquery.Client(project=project_id)

    bucket_uri = f"gs://{bucket_name}/{source_folder}/{table_id}_*.json"

    # Create the full table reference
    table_ref = client.dataset(dataset_id).table(table_id)

    schema = [
        bigquery.SchemaField("element", "INTEGER", mode="REQUIRED"),
        # Store raw JSON in a STRING field
        bigquery.SchemaField("data", "JSON", mode="REQUIRED"),
    ]

    # Define the Load Job Configuration
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        # or WRITE_TRUNCATE if overwriting
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=schema
    )

    # Partitioning and Clustering
    job_config.range_partitioning = bigquery.RangePartitioning(
        field="element",
        range_=bigquery.PartitionRange(
            start=1,
            end=2000,   # Example: upper bound above max player_id
            interval=1,
        )
    )
    # job_config.clustering_fields = ["gameweek"]

    # Start the load job
    load_job = client.load_table_from_uri(
        bucket_uri,
        table_ref,
        job_config=job_config,
    )

    load_job.result()  # Wait for the job to complete
    logging.info(
        f"Loaded {load_job.output_rows} rows into"
        f" {dataset_id}:{table_id}.")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for verbose logs
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Upload data to BigQuery table.")
    parser.add_argument(
        "--table",
        type=str,
        default="element_summary_history",
        help="The BigQuery table name in the format table (e.g., my_table)"
    )
    args = parser.parse_args()

    BUCKET = os.getenv("BUCKET_ID")
    PROJECT = os.getenv("PROJECT_ID")
    DATASET = os.getenv("DATASET_ID")

    upload_element_summary_from_gcs_to_bigquery(
        project_id=PROJECT,
        dataset_id=DATASET,
        bucket_name=BUCKET,
        source_folder='element_summary',
        table_id=args.table
    )
