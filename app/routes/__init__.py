from app.routes.links import router as links_router
from app.routes.stats import router as stats_router
from app.routes.redirect import router as redirect_router

__all__ = ["links_router", "stats_router", "redirect_router"]
