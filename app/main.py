from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import redis
import sqlite3
import os
import datetime
import json

app = FastAPI(title="Catty Reminders v4.0", version="4.0.0")
templates = Jinja2Templates(directory="templates")
# Redis подключение для счетчика
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# SQLite база для демонстрации
DB_PATH = "/app/data/catty.db"

def init_database():
    """Инициализация простой БД"""
    os.makedirs("/app/data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
# Инициализируем БД при старте
init_database()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Главная страница - логин форма"""
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Дашборд после логина"""
    # Получаем статистику
    visit_count = redis_client.get('total_visits') or 0
    task_count = get_task_count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "visit_count": visit_count,
        "task_count": task_count,
        "containers": ["web", "redis", "database"],
        "deployment_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/api/visits")
def get_visits():
    """API: получить количество посещений"""
    visits = redis_client.get('total_visits') or 0
    return {"visits": int(visits), "timestamp": datetime.datetime.now().isoformat()}
@app.post("/api/visit")
def increment_visit(request: Request):
    """API: увеличить счетчик посещений"""
    try:
        # Redis счетчик
        visits = redis_client.incr('total_visits')
        
        # SQLite логирование
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO visits (user_agent, ip_address) VALUES (?, ?)",
            (request.headers.get('user-agent', ''), request.client.host)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "visits": visits}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_task_count():
    """Получить количество задач из БД"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0
@app.get("/api/stats")
def get_stats():
    """Полная статистика системы"""
    visits = redis_client.get('total_visits') or 0
    task_count = get_task_count()
    
    # Получаем последние посещения
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MAX(timestamp) FROM visits")
    db_stats = cursor.fetchone()
    conn.close()
    
    return {
        "app": "Catty Reminders v4.0",
        "lab": 4,
        "visits": int(visits),
        "tasks": task_count,
        "database_records": db_stats[0] if db_stats else 0,
        "last_activity": db_stats[1] if db_stats else None,
        "containers": 2,
        "deployment": "Docker Compose",
        "ci_cd": "GitHub Actions",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    redis_ok = redis_client.ping()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        db_ok = True
    except:
        db_ok = False
    
    return {
        "status": "healthy" if redis_ok and db_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": datetime.datetime.now().isoformat()
    }
# Добавим несколько тестовых задач при первом запуске
@app.on_event("startup")
def startup_event():
    """Действия при запуске приложения"""
    # Устанавливаем начальное значение счетчика если его нет
    if not redis_client.exists('total_visits'):
        redis_client.set('total_visits', 100)  # Начинаем со 100
    
    # Добавляем тестовые задачи если БД пустая
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        test_tasks = [
            ("Complete Lab 4", "Docker Compose deployment"),
            ("Setup CI/CD", "GitHub Actions workflow"),
            ("Add Redis cache", "Visit counter implementation"),
            ("Deploy to production", "Course server deployment")
        ]
        cursor.executemany("INSERT INTO tasks (title, description) VALUES (?, ?)", test_tasks)
        conn.commit()
    conn.close()
