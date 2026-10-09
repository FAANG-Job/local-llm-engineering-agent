from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from logging_config import get_logger, configure_logging
from app.models.goods_receipt import Receipt

COLLECTION = settings.QDRANT_RECEIPT
qdrant = QdrantClient(url=settings.QDRANT_URL)
configure_logging()
logger = get_logger(__name__)

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
