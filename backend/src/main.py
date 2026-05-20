"""FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler"""
    # Startup
    print("🚀 Smart Customer Service API is starting...")
    print(f"📝 Debug mode: {settings.debug}")
    print(f"🔗 Frontend URL: {settings.frontend_url}")
    
    yield
    
    # Shutdown
    print("👋 Smart Customer Service API is shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title="Smart Customer Service API",
    description="智能客服系统后端 API",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug
    )
