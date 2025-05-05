import os
from pydantic import BaseModel, Field
from pydantic import StrictStr


class Config(BaseModel):
    project_id: StrictStr = Field(
        ...,
        description="Google Cloud Project ID"
    )
    bucket_name: StrictStr = Field(
        ...,
        description="Google Cloud Storage bucket name"
    )
    dataset_id: StrictStr = Field(
        ...,
        description="BigQuery dataset ID"
    )

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        try:
            return cls(
                project_id=os.getenv('PROJECT_ID'),
                bucket_name=os.getenv('BUCKET_ID'),
                dataset_id=os.getenv('DATASET_ID')
            )
        except ValueError as e:
            raise ValueError(f"Configuration error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
