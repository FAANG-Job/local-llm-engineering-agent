from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from cosine_similarity import get_embeddings
from logging_config import configure_logging, get_logger
from app.models.policy_chunk import PolicyChunk

COLLECTION = settings.QDRANT_POLICY
qdrant = QdrantClient(url=settings.QDRANT_URL)
configure_logging()
logger = get_logger(__name__)


policy_chunks = [
    PolicyChunk(
        policy_id="AP-001",
        document_id="invoice_matching_policy.txt",
        section="1: Quantity Matching",
        text=(
            "Quantity Matching: Invoiced quantity must not exceed "
            "the total quantity recorded as received against the "
            "purchase order. If it exceeds received quantity, "
            "recommend investigation with the receiving team."
        ),
    ),
    PolicyChunk(
        policy_id="AP-001",
        document_id="invoice_matching_policy.txt",
        section="2: Price Matching",
        text=(
            "Price Matching: Invoice unit price must equal the "
            "purchase order unit price in the same currency. "
            "Any price difference requires procurement review."
        ),
    ),
    PolicyChunk(
        policy_id="AP-001",
        document_id="invoice_matching_policy.txt",
        section="3: Missing Receipts",
        text=(
            "Missing Receipts: If no goods receipt exists for the "
            "purchase order, report missing receiving evidence "
            "and recommend checking with the receiving team. "
            "Do not assume that goods were delivered."
        ),
    ),
    PolicyChunk(
        policy_id="AP-001",
        document_id="invoice_matching_policy.txt",
        section="4: Action Restrictions",
        text=(
            "Action Restrictions: The agent may retrieve records, "
            "investigate discrepancies and recommend actions. "
            "It must not approve payments or modify business records."
        ),
    ),
]


def insert_policy():
    if not qdrant.collection_exists(COLLECTION):
        logger.info("Creating policy vector collection")
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE,
            ),
        )

    for point_id, policy_chunk in enumerate(policy_chunks, start=104):
        embedding_vector = get_embeddings(policy_chunk.text)
        qdrant.upsert(
            collection_name=COLLECTION,
            wait=True,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding_vector,
                    payload=policy_chunk.model_dump(mode="json"),
                )
            ],
        )


if __name__ == "__main__":
    insert_policy()
