import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
_client = None

def _is_atlas(uri: str) -> bool:
    return "mongodb.net" in uri  # Atlas hosts

async def get_db():
    """
    Returns an AsyncIOMotorDatabase.
    For Atlas: use certifi CA and disable OCSP endpoint check (common on Windows/corp networks).
    For localhost: plain connection.
    """
    global _client
    uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/newsagg")

    if _client is None:
        if _is_atlas(uri):
            import certifi
            _client = AsyncIOMotorClient(
                uri,
                tls=True,
                tlsCAFile=certifi.where(),
                tlsDisableOCSPEndpointCheck=True,  # keep this, remove tlsAllowInvalidCertificates entirely
                appName="NewsAgg",
            )
        else:
            _client = AsyncIOMotorClient(uri, appName="NewsAgg")

    db = _client.get_default_database()
    if db is None:
        db = _client["newsagg"]
    return db
