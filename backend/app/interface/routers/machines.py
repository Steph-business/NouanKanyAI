from fastapi import APIRouter

from app.services.demo_data import load_demo_machine_state

router = APIRouter()


@router.get("/machines")
def list_machines():
    return load_demo_machine_state()
