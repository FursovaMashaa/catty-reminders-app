# app/routers/root.py
"""
This module provides routes for the main pages.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

from app import templates
from app.utils.auth import get_storage_for_page
from app.utils.mysql_storage import MySQLStorage

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
import mysql.connector
from app import db_config


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------
@router.get("/")
async def read_root(request: Request):
    """Корневой путь - перенаправляем на логин или показываем инфо."""
    return RedirectResponse(url="/login")
@router.get(
    path="/",
    summary="Gets the main page",
    tags=["Pages"],
    response_class=HTMLResponse
)
async def read_root(
    request: Request,
    storage: MySQLStorage = Depends(get_storage_for_page)
):
    """Главная страница с информацией о Lab 4."""
    
    # Проверяем подключение к БД
    db_status = "✅ Connected"
    try:
        # Простая проверка - пытаемся выполнить запрос
        test_query = "SELECT 1 as test"
        storage.cursor.execute(test_query)
        result = storage.cursor.fetchone()
        if result and result['test'] == 1:
            db_status = "✅ MySQL Connected"
        else:
            db_status = "⚠️ MySQL Check Failed"
    except Exception as e:
        db_status = f"❌ MySQL Error: {str(e)[:50]}"
    
    # Получаем базовую статистику
    try:
        lists_count = len(storage.get_lists())
        total_items = sum(len(storage.get_items(lst.id)) for lst in storage.get_lists())
    except:
        lists_count = 0
        total_items = 0
    
    context = {
        'request': request,
        'owner': storage.owner,
        'lab4_info': {
            'title': 'Docker Compose - Lab 4',
            'description': 'Мультиконтейнерное приложение с MySQL',
            'features': [
                '✓ 2 Docker контейнера (App + MySQL)',
                '✓ Данные сохраняются в Docker Volume',
                '✓ Контейнеры общаются через Docker Network',
                '✓ Нет bind mount исходного кода',
                '✓ Health checks для БД'
            ],
            'db_status': db_status,
            'lists_count': lists_count,
            'total_items': total_items
        }
    }
    
    return templates.TemplateResponse("pages/index.html", context)
