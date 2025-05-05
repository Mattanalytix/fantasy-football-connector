from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ElementSummaryRequest(BaseModel):
    destination_folder: Optional[str] = Field(
        "element_summary", description="Destination folder in the bucket")
    team_ids: Optional[List[int]] = Field(
        None, description="List of team IDs to filter elements")
    element_ids: Optional[List[int]] = Field(
        None, description="List of element IDs to filter elements")
    max_workers: Optional[int] = Field(
        5, description="Number of workers for parallel processing")

    @field_validator('destination_folder')
    def validate_destination_folder(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("destination_folder must be a non-empty string")
        return v

    @field_validator('max_workers')
    def validate_max_workers(cls, v):
        if v < 1:
            raise ValueError("max_workers must be at least 1")
        if v > 20:
            raise ValueError("max_workers cannot exceed 100")
        return v


class ElementFromTeamRequest(BaseModel):
    team_id: int = Field(description="Team ID to filter elements")

    @field_validator('team_id')
    def validate_team_id(cls, v):
        if v < 1 or v > 19:
            raise ValueError("team_id must be in the range 1-19")
        return v
