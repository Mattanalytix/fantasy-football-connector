from google.cloud import storage
import json


def upload_json_to_gcs(bucket_name: str, blob_name: str, data: dict) -> None:
    """Uploads a JSON object to a specified GCS bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    ndjson_content = "\n".join(json.dumps(record) for record in data)
    blob.upload_from_string(ndjson_content, content_type="application/json")
