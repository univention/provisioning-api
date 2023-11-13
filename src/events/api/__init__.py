from fastapi import APIRouter

from .v1 import router as router_v1

name = "/events"
v1_prefix = f"{name}/v1"

router = APIRouter()
router.include_router(router_v1, prefix=v1_prefix)
