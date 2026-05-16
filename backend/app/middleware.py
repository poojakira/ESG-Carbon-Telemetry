from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler # type: ignore
from slowapi.util import get_remote_address # type: ignore
from slowapi.errors import RateLimitExceeded # type: ignore
import logging
import traceback
import time

limiter = Limiter(key_func=get_remote_address)

async def error_handling_middleware(request: Request, call_next):
    """ Global middleware to catch all unhandled exceptions and return structured JSON. """
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details in structured format
        logging.info(f"API Request: {request.method} {request.url.path} | Status: {response.status_code} | Latency: {process_time:.4f}s")
        return response
    except Exception as e:
        logging.error(f"💥 GLOBAL UNHANDLED EXCEPTION: {str(e)}")
        logging.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "CRITICAL_FAULT",
                "message": "An internal industrial kernel error occurred.",
                "detail": str(e) if request.app.debug else "Internal Stability Breach",
                "trace_id": str(time.time())
            }
        )

def setup_middlewares(app):
    """ Configures the application with security middleware. """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.middleware("http")(error_handling_middleware)
