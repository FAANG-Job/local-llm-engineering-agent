from pydantic import BaseModel, Field


class Receipt(BaseModel):
    receipt_id: str = Field(
        min_length=1,
        description="Record company creates when goods arrive from the supplier.",
    )
    po_id: str = Field(min_length=1, description="Raised purchase order")
    quantity_received: int = Field(
        gt=0, strict=True, description="No of Item to be received by customer"
    )
