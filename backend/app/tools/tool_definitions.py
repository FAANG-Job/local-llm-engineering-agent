GET_INVOICE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_invoice",
        "description": (
            "Retrieve invoice details using an exact invoice ID. "
            "The result includes the linked purchase order ID, "
            "quantity, unit price and currency."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_id": {
                    "type": "string",
                    "description": "Invoice reference, such as INV-104",
                }
            },
            "required": ["invoice_id"],
            "additionalProperties": False,
        },
    },
}

TOOLS = [GET_INVOICE_TOOL]
