from fastapi import APIRouter

from app.api.endpoints import auth, categorias, combos, ofertas, pedidos, productos, users

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["categorias"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(ofertas.router, prefix="/ofertas", tags=["ofertas"])
api_router.include_router(combos.router, prefix="/combos", tags=["combos"])
api_router.include_router(pedidos.router, prefix="/pedidos", tags=["pedidos"])
