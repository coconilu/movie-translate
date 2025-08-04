"""
FastAPI backend server for Movie Translate
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from movie_translate.api import app
from movie_translate.core import logger, settings


def main():
    """Run the FastAPI backend server"""
    parser = argparse.ArgumentParser(description="Movie Translate API Server")
    parser.add_argument("--host", default=settings.api.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.api.port, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Movie Translate API server on {args.host}:{args.port}")
    
    # Import uvicorn here to avoid circular imports
    import uvicorn
    
    uvicorn.run(
        "movie_translate.api.backend:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()