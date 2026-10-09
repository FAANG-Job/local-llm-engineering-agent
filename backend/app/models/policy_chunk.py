from pydantic import BaseModel, Field


class PolicyChunk(BaseModel):
    policy_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    section: str = Field(min_length=1)
    text: str = Field(min_length=1)
