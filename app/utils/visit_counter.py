import os
from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "mysql://root:mypass@db:3306/catty_reminders")
engine = create_engine(DATABASE_URL)

def init_visit_counter():
    """Инициализирует таблицу для счётчика посещений"""
    try:
        with engine.connect() as conn:
            # Создаем таблицу если её нет
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS visit_counter (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    visits INT DEFAULT 0,
                    last_visit DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """))
            
            # Инициализируем счетчик если нет записей
            result = conn.execute(text("SELECT COUNT(*) FROM visit_counter"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO visit_counter (visits, last_visit) VALUES (0, NOW())"))
                print("✅ Visit counter initialized with first record")
            
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Visit counter initialization error: {e}")
        return False

def increment_visit():
    """Увеличивает счётчик посещений на 1 и возвращает новое значение"""
    try:
        with engine.connect() as conn:
            # Увеличиваем счетчик
            conn.execute(text("UPDATE visit_counter SET visits = visits + 1, last_visit = NOW() WHERE id = 1"))
            conn.commit()
            
            # Получаем обновленное значение
            result = conn.execute(text("SELECT visits, last_visit FROM visit_counter WHERE id = 1"))
            row = result.fetchone()
            
            if row:
                return {
                    "visits": row[0],
                    "last_visit": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else None
                }
            return {"visits": 0, "last_visit": None}
    except Exception as e:
        print(f"❌ Error incrementing visit counter: {e}")
        return {"visits": 0, "last_visit": None}

def get_visit_stats():
    """Получает текущую статистику посещений"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT visits, last_visit FROM visit_counter WHERE id = 1"))
            row = result.fetchone()
            
            if row:
                return {
                    "total_visits": row[0],
                    "last_visit": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else None,
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            return {"total_visits": 0, "last_visit": None, "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        print(f"❌ Error getting visit stats: {e}")
        return {"total_visits": 0, "last_visit": None, "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
