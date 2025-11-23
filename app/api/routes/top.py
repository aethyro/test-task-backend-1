from fastapi import APIRouter

from . import health, pull_requests, teams, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(teams.router)
api_router.include_router(users.router)
api_router.include_router(pull_requests.router)
