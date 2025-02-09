from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Depends
import psycopg2
import os
from typing import List
from pydantic import BaseModel #Для валидации данных
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:8000",  # Разрешить запросы с вашего frontend (укажите правильный порт)
    "http://localhost",       # Для разработки
    "http://127.0.0.1",        # Альтернативный localhost
    "*",                       # Только для разработки! В продакшене укажите конкретные домены
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP-методы
    allow_headers=["*"],  # Разрешить все заголовки
)

def get_db_connection():
    """Получает соединение с базой данных."""
    try:
        url = urlparse(os.environ.get("postgresql://postgress:0xswhKnCeYNz4aSOmVYFrpPst0au0gMR@dpg-cujue5jv2p9s73871dog-a/mosh"))
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode='require' if url.hostname != 'localhost' else 'prefer'
        )
        return conn
    except psycopg2.Error as e:
        print(f"Не удалось установить соединение с базой данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подключения к базе данных")


def execute_query(conn, sql, params=None):
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Ошибка при выполнении запроса: {e}")
        raise HTTPException(status_code=500, detail="Ошибка выполнения запроса")
    finally:
        if cursor:
            cursor.close()

# 1. Эндпоинт для регистрации пользователя
class UserRegistration(BaseModel):
    login: str
    password: str

@app.get("/create/bd")
def create_table():
    """Создает таблицу 'users_' в базе данных."""
    conn = None  # Инициализируем conn вне блока try
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # SQL-запрос для создания таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users_ (
            user_id SERIAL PRIMARY KEY,
            login_ VARCHAR(255) UNIQUE NOT NULL,
            password_ VARCHAR(255) NOT NULL,
            item_use_id INT[],
            access_ TEXT,
            req_id INT[],
            req_repair_id INT[]
        );
        """

        cur.execute(create_table_query)

        conn.commit()  # Сохраняем изменения в базе данных
        print("Таблица 'users_' успешно создана.")

    except (psycopg2.Error, ValueError) as e:
        print(f"Ошибка при создании таблицы: {e}")
        if conn:
            conn.rollback()  # Откатываем транзакцию в случае ошибки
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.post("/reg_user")
async def reg_user(user: UserRegistration):
    """Регистрирует нового пользователя."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(MAX(user_id), 0) + 1 FROM users_")
        user_id = cursor.fetchone()[0]

        sql = "INSERT INTO users_ (user_id, login_, password_, access_) VALUES (%s, %s, %s, %s)"
        params = (user_id, user.login, user.password, "user") # Используем user.login и user.password
        execute_query(conn, sql, params)

        return {"message": "Пользователь успешно зарегистрирован", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 2. Эндпоинт для добавления товара
@app.post("/add_item")
def add_item(name_item: str, count: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(MAX(item_id), 0) + 1 FROM items_")
        item_id = cursor.fetchone()[0]

        sql = "INSERT INTO items_ (item_id, name_item, count) VALUES (%s, %s, %s)"
        params = (item_id, name_item, count)
        execute_query(conn, sql, params)

        return {"message": "Товар успешно добавлен", "item_id": item_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 3. Эндпоинт для добавления плана закупки
@app.post("/add_plan_buy")
def add_plan_buy(name_item: str, price: int, name_prov: str):
    conn = None
    try:
        conn = get_db_connection()

        sql = "INSERT INTO plan_buy_item_ (name_item, price, name_prov) VALUES (%s, %s, %s)"
        params = (name_item, price, name_prov)
        execute_query(conn, sql, params)

        return {"message": "План закупки успешно добавлен"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 4. Эндпоинт для добавления запроса на товар
@app.post("/add_request_item")
def add_request_item(user_id: int, name_item: str):
    conn = None
    try:
        conn = get_db_connection()

        sql = "INSERT INTO request_item_ (user_id, name_item_) VALUES (%s, %s)"
        params = (user_id, name_item)
        execute_query(conn, sql, params)

        return {"message": "Запрос на товар успешно добавлен"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 5. Эндпоинт для добавления запроса на ремонт
@app.post("/add_request_repair")
def add_request_repair(name_item: str):
    conn = None
    try:
        conn = get_db_connection()

        sql = "INSERT INTO request_repair_ (name_item) VALUES (%s)"
        params = (name_item,)
        execute_query(conn, sql, params)

        return {"message": "Запрос на ремонт успешно добавлен"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 6. Эндпоинт для принятия запроса на товар
@app.put("/accept_request_item")
async def accept_request_item(user_id: int, name_item: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id FROM items_ WHERE name_item = %s", (name_item,))
        item_id_result = cursor.fetchone()

        if item_id_result is None:
            raise HTTPException(status_code=404, detail="Товар не найден")

        item_id = item_id_result[0]

        sql = "UPDATE users_ SET item_use_id = %s WHERE user_id = %s"
        params = (item_id, user_id)
        execute_query(conn, sql, params)

        return {"message": f"Запрос на товар {name_item} для пользователя {user_id} принят"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# 7. Эндпоинт для изменения количества товара на складе
@app.put("/reduct_inv")
async def reduct_inv(name_item: str, **kwargs):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        allowed_fields = ("count", "price", "description")

        update_values = []
        params = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                update_values.append(f"{key} = %s")
                params.append(value)
            else:
                raise HTTPException(status_code=400, detail=f"Недопустимое поле: {key}")

        if not update_values:
            raise HTTPException(status_code=400, detail="Нет допустимых полей для обновления")

        sql = f"UPDATE items_ SET {', '.join(update_values)} WHERE name_item = %s"
        params.append(name_item)

        execute_query(conn, sql, params)

        return {"message": f"Товар {name_item} успешно обновлен"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# GET endpoints
@app.get("/")
async def home():
    return "HIIIIII"


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, login_, access_ FROM users_ WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user_data = {
            "user_id": user[0],
            "login_": user[1],
            "access_": user[2]
        }

        return user_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id, name_item, count, price, description FROM items_ WHERE item_id = %s", (item_id,))
        item = cursor.fetchone()

        if item is None:
            raise HTTPException(status_code=404, detail="Товар не найден")

        item_data = {
            "item_id": item[0],
            "name_item": item[1],
            "count": item[2],
            "price": item[3],
            "description": item[4]
        }

        return item_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

@app.get("/items")
async def get_all_items():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT item_id, name_item, count, price, description FROM items_")
        items = cursor.fetchall()

        item_list = []
        for item in items:
            item_data = {
                "item_id": item[0],
                "name_item": item[1],
                "count": item[2],
                "price": item[3],
                "description": item[4]
            }
            item_list.append(item_data)

        return item_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

#PUT Endpoints
class ItemUpdate(BaseModel):
    name_item: str
    count: int
    price: float
    description: str

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE items_
            SET name_item = %s, count = %s, price = %s, description = %s
            WHERE item_id = %s
        """
        params = (item.name_item, item.count, item.price, item.description, item_id)
        execute_query(conn, sql, params)

        return {"message": f"Товар {item_id} успешно обновлен"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
      if conn:
        conn.close()

# Пример структуры таблицы (users_):
"""
CREATE TABLE users_ (
    user_id SERIAL PRIMARY KEY,
    login_ VARCHAR(255) NOT NULL,
    password_ VARCHAR(255) NOT NULL,
    access_ VARCHAR(20) NOT NULL,
    item_use_id INT
);

Пример структуры таблицы (items_):
CREATE TABLE items_ (
    item_id SERIAL PRIMARY KEY,
    name_item VARCHAR(255) NOT NULL,
    count INT,
    price DECIMAL(10, 2),
    description TEXT
);

Пример структуры таблицы (plan_buy_item_):
CREATE TABLE plan_buy_item_ (
    plan_id SERIAL PRIMARY KEY,
    name_item VARCHAR(255) NOT NULL,
    price INT NOT NULL,
    name_prov VARCHAR(255) NOT NULL
);

Пример структуры таблицы (request_item_):
CREATE TABLE request_item_ (
    request_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name_item_ VARCHAR(255) NOT NULL
);

Пример структуры таблицы (request_repair_):
CREATE TABLE request_repair_ (
    request_id SERIAL PRIMARY KEY,
    name_item VARCHAR(255) NOT NULL
);
"""