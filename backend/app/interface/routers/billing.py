from fastapi import APIRouter

router = APIRouter()


@router.get("/billing")
def get_billing():
    return {
        "grossSavings": 125000.0,
        "gainShare": 12500.0,
        "barData": [{"name": "W1", "savings": 18000.0}],
        "auditTrail": [],
        "invoices": [],
    }
