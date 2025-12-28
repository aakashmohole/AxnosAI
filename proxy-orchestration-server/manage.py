from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import httpx
import jwt

app = FastAPI()

JWT_SECRET = "18YfNx88BNLoNASQR2DItRS8JHn5WErq"  # same as NestJS JWT_ACCESS_SECRET
JWT_ALGORITHM = "HS256"

# Config
# NESTJS_VALIDATE_URL = "http://localhost:3000/v1/auth/login"  # endpoint to check JWT
DJANGO_API_URL = "http://localhost:8000"

# Extract user info from payload
def extract_user_info_from_payload(payload :  dict):
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if not user_id and isinstance(payload.get("data"), dict):
        user_id = payload["data"].get("_id")
        print("[PROXY]: Extracted user_id from nested data:", user_id)
    email = payload.get("email") or (payload.get("data") or {}).get("email")
    print("[PROXY]: Extracted user info - user_id:", user_id, "email:", email)
    return user_id, email

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_django(full_path: str, request: Request):
    
    #  Get access token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="[PROXY]: Authorization header missing")
    
    token = auth_header.split(" ")[1]

    #  Validate JWT directly
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # payload has user info like "sub" and "email"
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="[PROXY]: Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="[PROXY]: Invalid token")
    
    
    user_id, email = extract_user_info_from_payload(payload)
    if not user_id:
        raise HTTPException(status_code=400, detail = "[PROXY]: User ID not found in token")
    

     # 3 Forward request to Django
    async with httpx.AsyncClient(timeout=60.0) as client:
        django_url = f"{DJANGO_API_URL}/{full_path}"
        method = request.method
        headers = dict(request.headers)
        headers.pop("host", None)
        body = await request.body()

        headers["X-User-ID"] = str(user_id)
        if email:
            headers["X-User-Email"] = str(email)

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