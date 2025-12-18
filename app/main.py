"""
This module is the main module for the FastAPI app.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

from app.utils.exceptions import UnauthorizedPageException
from app.utils.visit_counter import init_visit_counter, increment_visit, get_visit_stats
from app.routers import api, login, reminders, root

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time


# --------------------------------------------------------------------------------
# Middleware for visit counting
# --------------------------------------------------------------------------------

class VisitCounterMiddleware(BaseHTTPMiddleware):
    """Middleware to count page visits."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip counting for static files, API calls, and certain paths
        skip_paths = [
            '/static/', '/api/', '/favicon.ico', 
            '/health', '/stats', '/visits', '/reset-counter'
        ]
        
        should_count = (
            request.method == "GET" and
            not any(request.url.path.startswith(path) for path in skip_paths) and
            not request.url.path.endswith(('.css', '.js', '.png', '.jpg', '.ico'))
        )
        
        if should_count:
            increment_visit()
        
        # Add visit stats to request state for use in templates
        request.state.visit_stats = get_visit_stats()
        
        response = await call_next(request)
        return response


# --------------------------------------------------------------------------------
# App Creation
# --------------------------------------------------------------------------------

app = FastAPI()

# Add visit counter middleware
app.add_middleware(VisitCounterMiddleware)

# Initialize visit counter on startup
@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup."""
    print("🚀 Starting Catty Reminders App...")
    
    # Initialize visit counter
    if init_visit_counter():
        print("✅ Visit counter initialized successfully")
    else:
        print("⚠️ Visit counter initialization had issues")
    
    # Show initial stats
    stats = get_visit_stats()
    print(f"📊 Initial visit count: {stats.get('total_visits', 0)}")


# Include routers
app.include_router(root.router)
app.include_router(api.router)
app.include_router(login.router)
app.include_router(reminders.router)


# --------------------------------------------------------------------------------
# New routes for visit statistics
# --------------------------------------------------------------------------------

@app.get("/stats")
async def stats_page(request: Request):
    """Display visit statistics page."""
    stats = get_visit_stats()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catty Reminders - Statistics</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            .stats-container {{
                max-width: 600px;
                margin: 50px auto;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .stat-item {{
                margin: 15px 0;
                padding: 10px;
                background: white;
                border-radius: 8px;
                border-left: 4px solid #4CAF50;
            }}
            .stat-label {{
                font-weight: bold;
                color: #333;
            }}
            .stat-value {{
                color: #2196F3;
                font-size: 1.2em;
                margin-left: 10px;
            }}
            .visit-count {{
                font-size: 2em;
                color: #FF5722;
                text-align: center;
                margin: 20px 0;
            }}
            .db-status {{
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.9em;
            }}
            .db-connected {{ background: #d4edda; color: #155724; }}
            .db-disconnected {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="stats-container">
            <h1>📊 Lab 4 - Docker Compose Statistics</h1>
            <p>This demonstrates multi-container application with persistent data storage.</p>
            
            <div class="visit-count">
                Total Visits: <strong>{stats.get('total_visits', 0)}</strong>
            </div>
            
            <div class="stat-item">
                <span class="stat-label">Last Visit:</span>
                <span class="stat-value">{stats.get('last_visit', 'Never')}</span>
            </div>
            
            <div class="stat-item">
                <span class="stat-label">Current Time:</span>
                <span class="stat-value">{stats.get('current_time', 'N/A')}</span>
            </div>
            
            <div class="stat-item">
                <span class="stat-label">Database Status:</span>
                <span class="stat-value db-status {stats.get('database', 'disconnected')}">
                    {stats.get('database', 'disconnected').upper()}
                </span>
            </div>
            
            <div style="margin-top: 30px; font-size: 0.9em; color: #666;">
                <p><strong>Lab 4 Features Demonstrated:</strong></p>
                <ul>
                    <li>✓ Multi-container architecture (App + MySQL)</li>
                    <li>✓ Persistent data storage with Docker volumes</li>
                    <li>✓ Service communication via Docker network</li>
                    <li>✓ Health checks and dependencies</li>
                    <li>✓ No bind mounts (proper container isolation)</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/" class="btn btn-primary">Back to Main Page</a>
               
