from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import httpx
import jwt

app = FastAPI()

JWT_SECRET = "supersecret"  # same as NestJS JWT_ACCESS_SECRET
JWT_ALGORITHM = "HS256"

# Config
# NESTJS_VALIDATE_URL = "http://localhost:3000/v1/auth/login"  # endpoint to check JWT
DJANGO_API_URL = "http://localhost:8000"

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_django(full_path: str, request: Request):
    
    #  Get access token from Authorization header
    
    print(full_path)
    auth_header = request.headers.get("Auth orization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = auth_header.split(" ")[1]

    #  Validate JWT directly
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(payload['email'])
        # payload has user info like "sub" and "email"
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
     # 3 Forward request to Django
    async with httpx.AsyncClient() as client:
        django_url = f"{DJANGO_API_URL}/{full_path}"
        method = request.method
        headers = dict(request.headers)
        headers.pop("host", None)
        body = await request.body()

        django_resp = await client.request(
            method,
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