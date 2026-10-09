from logging_config import get_logger,configure_logging
from settings import settings
from qdrant_client import QdrantClient, models

COLLECTION = settings.QDRANT_INVOICE
configure_logging()
qdrant = QdrantClient(url=settings.QDRANT_URL)
logger = get_logger(__name__)

get_invoice(invoice_id:str):
    logger.info("get_invoice() is called")
    qdrant.
