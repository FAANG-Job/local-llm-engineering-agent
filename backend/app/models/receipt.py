from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from logging_config import get_logger, configure_logging

COLLECTION = settings.QDRANT_RECEIPT
qdrant = QdrantClient(url=settings.QDRANT_URL)
configure_logging()
logger = get_logger(__name__)


class Receipt(BaseModel):
    receipt_id: str = Field(
        min_length=1,
        description="Record company creates when goods arrive from the supplier.",
    )
    po_id: str = Field(min_length=1, description="Raised purchase order")
    quantity_received: int = Field(
        gt=0, strict=True, description="No of Item to be received by customer"
    )


def insert_receipt():

    if not qdrant.collection_exists(COLLECTION):
        logger.info("Create Database table ")
        qdrant.create_collection(
            collection_name=COLLECTION,
        )
    point_id = 204
    receipt = Receipt(
        receipt_id="REC-104",
        po_id="PO-104",
        quantity_received=80,
    )
    qdrant.upsert(
        collection_name=COLLECTION,
        wait=True,
        points=[
            models.PointStruct(
                id=point_id,
                vector={},
                payload=receipt.model_dump(mode="json"),
            )
        ],
    )


if __name__ == "__main__":
    insert_receipt()
