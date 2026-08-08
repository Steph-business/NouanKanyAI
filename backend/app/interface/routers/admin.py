from fastapi import APIRouter

router = APIRouter()


@router.get("/admin")
def admin_health():
    return {
        "status": "ok",
        "activeMachines": 4,
        "alerts": 1,
        "efficiency": 87.5,
    }
