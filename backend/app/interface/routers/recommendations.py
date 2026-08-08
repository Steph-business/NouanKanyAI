from fastapi import APIRouter

router = APIRouter()


@router.get("/recommendations")
def get_recommendations():
    return {
        "recommendations": [
            "Vérifier la pression de la pompe hydraulique",
            "Optimiser la programmation de la climatisation",
        ],
        "count": 2,
    }
