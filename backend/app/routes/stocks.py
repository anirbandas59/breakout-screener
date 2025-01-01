from fastapi import APIRouter

router = APIRouter()


@router.get("/fetch-scripts")
def fetch_scripts():
    """
    Logic to scrape or fetch scripts from NSE
    """
    return {
        "message": "Fetched list successfully"
    }
