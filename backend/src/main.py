"""FastAPI Application Entry Point using PyCore"""
from pycore.api import APIConfig, APIServer
from pycore.core import Logger, LoggerConfig, LogLevel, get_logger
from src.api.routes import health
from src.core.config import settings

# 配置日志
Logger.configure(LoggerConfig(
    level=LogLevel.INFO,
    app_name="smart-customer-service",
    json_format=False
))
logger = get_logger()

# 创建 APIServer 实例
server = APIServer(APIConfig(
    title="Smart Customer Service API",
    version="1.0.0",
    description="智能客服系统后端 API",
    host="0.0.0.0",
    port=settings.backend_port,
    debug=settings.debug,
    cors_origins=[settings.frontend_url, "http://localhost:5173"],
))

# 启动事件处理器
def init_app():
    """应用启动初始化"""
    logger.info("🚀 Smart Customer Service API is starting...")
    logger.info("Debug mode", debug=settings.debug)
    logger.info("Frontend URL", frontend_url=settings.frontend_url)

def shutdown_app():
    """应用关闭清理"""
    logger.info("👋 Smart Customer Service API is shutting down...")

server.on_startup(init_app)
server.on_shutdown(shutdown_app)

# 注册路由
server.include_router(health.router)

# 导出 app 供 uvicorn 使用
app = server.app
