from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from logging_config import configure_logging, get_logger
from app.models.purchase_order import PurchaseOrder

COLLECTION = settings.QDRANT_PURCHASE_ORDERS
qdrant = QdrantClient(url=settings.QDRANT_URL)
configure_logging()
logger = get_logger(__name__)


def insert_purchase_order():

    if not qdrant.collection_exists(COLLECTION):
        logger.info("Create Database table ")
        qdrant.create_collection(
            collection_name=COLLECTION,
        )

    point_id = 104
    purchase_order = PurchaseOrder(
        po_id="PO-104",
        supplier_id="SUP-01",
        quantity=100,
        unit_price=500.00,
        currency="INR",
    )
    qdrant.upsert(
        collection_name=COLLECTION,
        wait=True,
        points=[
            models.PointStruct(
                id=point_id,
                vector={},
                payload=purchase_order.model_dump(mode="json"),
            )
        ],
    )


if __name__ == "__main__":
    insert_purchase_order()
