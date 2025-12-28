from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import jwt

app = FastAPI()

# ✅ CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = "18YfNx88BNLoNASQR2DItRS8JHn5WErq"
JWT_ALGORITHM = "HS256"

DJANGO_API_URL = "http://localhost:8000"

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_django(full_path: str, request: Request):

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(payload["email"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    async with httpx.AsyncClient() as client:
        django_url = f"{DJANGO_API_URL}/{full_path}"
        headers = dict(request.headers)
        headers.pop("host", None)

        body = await request.body()

        django_resp = await client.request(
            request.method,
            django_url,
            headers=headers,
            content=body,
            params=request.query_params,
        )

        return Response(
            content=django_resp.content,
            status_code=django_resp.status_code,
            headers=dict(django_resp.headers),
        )
