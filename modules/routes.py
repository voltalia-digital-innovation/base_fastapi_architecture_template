# modules/routes.py
from fastapi import APIRouter
from modules.core.routes import router as user_routes

"""
Centralizer router file for all modules

Author: Matheus Henrique (m.araujo)

Date: 3th September 2024
"""

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

# Include the user routes in the main router
router.include_router(user_routes)
