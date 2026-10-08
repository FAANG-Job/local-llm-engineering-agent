"""Data definitions and tool documentation for the local invoice agent POC.

Place this file in your application's models package, or split the classes
into separate files later. Requires Pydantic v2.

Scope: one item line per invoice and purchase order; positive integer units.
This file does not connect to Qdrant, execute tools, or run an agent.
"""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecordModel(BaseModel):
    """Reject unexpected fields and strip surrounding whitespace from strings."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Invoice(RecordModel):
    invoice_id: str = Field(min_length=1, description="Unique supplier invoice reference")
    po_id: str = Field(min_length=1, description="Reference to the linked purchase order")
    quantity: int = Field(gt=0, strict=True, description="Number of units billed")
    unit_price: Decimal = Field(
        ge=0, allow_inf_nan=False, description="Billed price per unit; store as a decimal string in Qdrant"
    )
    currency: str = Field(pattern=r"^[A-Z]{3}$", description="Three-letter currency code, such as INR")


class PurchaseOrder(RecordModel):
    po_id: str = Field(min_length=1, description="Unique purchase order reference")
    supplier_id: str = Field(min_length=1, description="Supplier reference")
    quantity: int = Field(gt=0, strict=True, description="Number of units ordered")
    unit_price: Decimal = Field(
        ge=0, allow_inf_nan=False, description="Agreed price per unit; store as a decimal string in Qdrant"
    )
    currency: str = Field(pattern=r"^[A-Z]{3}$", description="Three-letter currency code")


class GoodsReceipt(RecordModel):
    receipt_id: str = Field(min_length=1, description="Unique goods receipt reference")
    po_id: str = Field(min_length=1, description="Reference to the linked purchase order")
    quantity_received: int = Field(gt=0, strict=True, description="Units received in this delivery")


class PolicyChunk(RecordModel):
    policy_id: str = Field(min_length=1, description="Policy reference")
    document_id: str = Field(min_length=1, description="Source policy document reference")
    section: str = Field(min_length=1, description="Section reference for citations")
    text: str = Field(min_length=1, description="Policy text for this document chunk")


AGENT_DATA_CONTEXT = """
The POC uses single-line invoices and purchase orders.
An invoice's po_id identifies its linked purchase order.
Goods receipts link to a purchase order through po_id.
A purchase order can have multiple receipts; each represents a delivery.
An invoice quantity is units billed, PO quantity is units ordered, and
receipt quantity_received is units actually received in that delivery.
unit_price is a decimal string in JSON; use a Python tool for calculations.
Only compare monetary values in the same currency.
No receipt records means receiving evidence is missing, not proof of delivery.
Policy chunks contain document and section references for citing evidence.
The Qdrant point ID is separate from invoice_id, po_id, and receipt_id.
Policy embeddings are Qdrant vectors, not fields in the PolicyChunk payload.
""".strip()


def string_argument_schema(name: str, description: str) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {name: {"type": "string", "minLength": 1, "description": description}},
        "required": [name],
        "additionalProperties": False,
    }


def get_tool_documentation() -> list[dict[str, Any]]:
    """Return documentation to include in the agent's context.

    This is our own documentation format, not a native Ollama tools payload.
    Tool functions and dispatch must be implemented separately.
    """
    return [
        {
            "name": "get_invoice",
            "description": "Retrieve a supplier invoice by exact invoice ID, including its linked PO ID.",
            "input_schema": string_argument_schema("invoice_id", "Invoice reference, such as INV-104"),
            "output_schema": Invoice.model_json_schema(mode="serialization"),
        },
        {
            "name": "get_purchase_order",
            "description": "Retrieve the ordered quantity, agreed price, supplier, and currency by exact PO ID.",
            "input_schema": string_argument_schema("po_id", "Purchase order reference, such as PO-104"),
            "output_schema": PurchaseOrder.model_json_schema(mode="serialization"),
        },
        {
            "name": "get_receipts",
            "description": "Retrieve all goods receipts linked to a PO. An empty list means no recorded receipts.",
            "input_schema": string_argument_schema("po_id", "Purchase order reference"),
            "output_schema": {"type": "array", "items": GoodsReceipt.model_json_schema(mode="serialization")},
        },
        {
            "name": "search_policy",
            "description": "Search policy document chunks by semantic relevance and return text with source references.",
            "input_schema": string_argument_schema("query", "Question or search terms about the applicable policy"),
            "output_schema": {"type": "array", "items": PolicyChunk.model_json_schema(mode="serialization")},
        },
    ]


# After retrieving a Qdrant payload:
# invoice = Invoice.model_validate(point.payload)
# json_payload = invoice.model_dump(mode="json")
# This validates the record and serializes Decimal prices as JSON strings.
# References across records must be checked by your repository/tool code;
# these individual models do not enforce foreign keys or authorization.
