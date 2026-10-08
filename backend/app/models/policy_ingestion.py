from pydantic import BaseModel, Field
from settings import settings
from qdrant_client import QdrantClient, models
from cosine_similarity import get_embeddings
from logging_config import configure_logging, get_logger

COLLECTION = settings.QDRANT_POLICY
qdrant = QdrantClient(url=settings.QDRANT_URL)
configure_logging()
logger = get_logger(__name__)


class PolicyChunk(BaseModel):
    policy_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    section: str = Field(min_length=1)
    text: str = Field(min_length=1)


def insert_policy():
    policy_chunk = PolicyChunk(
        policy_id="AP-001",
        document_id="invoice_matching_policy.txt",
        section="1: Quantity Matching",
        text=(
            "Quantity Matching: Invoiced quantity must not exceed "
            "the total quantity recorded as received against the "
            "purchase order. If it exceeds received quantity, "
            "recommend investigation with the receiving team."
        ),
    )

    embedding_vector = get_embeddings(policy_chunk.text)
    logger.info(embedding_vector)

    if not qdrant.collection_exists(COLLECTION):
        logger.info("Creating policy vector collection")
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=len(embedding_vector),
                distance=models.Distance.COSINE,
            ),
        )

    qdrant.upsert(
        collection_name=COLLECTION,
        wait=True,
        points=[
            models.PointStruct(
                id=104,
                vector=embedding_vector,
                payload=policy_chunk.model_dump(mode="json"),
            )
        ],
    )


if __name__ == "__main__":
    insert_policy()
