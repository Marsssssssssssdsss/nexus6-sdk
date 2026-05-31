"""Anexus + FastAPI: Platform-side auth code verification.

Run:
    pip install anexus-verify fastapi uvicorn
    python examples/python/fastapi_platform.py

Test:
    curl -X POST http://localhost:8000/api/ai-action \
      -H "Content-Type: application/json" \
      -d '{"auth_code": "anx://shopify/user_abc123?exp=3600&ts=1717000000"}'
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anexus_verify import verify_code

app = FastAPI(title="My Platform API")

API_KEY = "nxs6_xxxxxxxxxxxx"


class AIRequest(BaseModel):
    auth_code: str
    action: str = ""


class AIResponse(BaseModel):
    access: str
    user: str
    can: list[str] = []


@app.post("/api/ai-action", response_model=AIResponse)
def handle_ai_request(req: AIRequest):
    """
    A user's AI agent sends an Anexus auth code.
    Verify it before granting access.
    """
    result = verify_code(code=req.auth_code, api_key=API_KEY)

    if not result.get("verified"):
        raise HTTPException(
            status_code=403,
            detail=result.get("error", "Invalid auth code"),
        )

    return AIResponse(
        access="granted",
        user=result["username"],
        can=result.get("permissions", []),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)