from fastapi import APIRouter

from app.api.endpoints import auth, combos, items, ofertas, productos, users

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(ofertas.router, prefix="/ofertas", tags=["ofertas"])
api_router.include_router(combos.router, prefix="/combos", tags=["combos"])
