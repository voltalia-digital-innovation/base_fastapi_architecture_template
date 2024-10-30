from fastapi import FastAPI
from modules.routes import router as api_routes
from fastapi.middleware.cors import CORSMiddleware
from modules.core.env import ALLOWED_ORIGINS, ALLOWED_ORIGINS_REGEX
from modules.core.middlewares.authentication import AuthenticationMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
)

# API Routes
app.include_router(api_routes)


@app.get("/api_check")
def api_check():
    """
    Method just to check application availability (used by Azure health check)

    Author: Matheus Henrique (m.araujo)

    Date: 3th September 2024
    """
    return 'Success!'
