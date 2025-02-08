# sport-inventory-app
### Шаг 1: Подготовка локального окружения

Клонируйте репозиторий с GitHub:
git clone https://github.com/leksika1/sport-inventory-app.git


cd sport-inventory-app # <имя_репозитория>




Создайте и активируйте виртуальное окружение:

python3 -m venv venv  # Создание

source venv/bin/activate  # Активация (Linux/macOS)

ИЛИ

.\venv\Scripts\activate  # Активация (Windows)


Установите зависимости:

pip install -r requirements.txt

### Шаг 2: Создание и настройка веб-сервиса на Render

Войдите в Render: Перейдите на сайт https://render.com/ и войдите в свою учетную запись.

Создайте новый веб-сервис: Нажмите кнопку “New +” и выберите “Web Service”.

Свяжите репозиторий GitHub:

Выберите свой аккаунт GitHub.

Выберите репозиторий с вашим проектом “Sport Inventory App”.

#### Настройте веб-сервис:
Name: Укажите имя для вашего веб-сервиса.

Environment: Выберите “Python 3”.

Branch: Выберите ветку для развертывания (обычно main).

Root Directory: Оставьте пустым (если ваш requirements.txt находится в корне проекта).

Runtime: python3

Build Command: pip install -r requirements.txt

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT (Важно! Render предоставляет порт через переменную окружения PORT)

Instance Type: Free

### Шаг 3: Настройка базы данных PostgreSQL на Render

#### Создайте базу данных PostgreSQL на Render:

Нажмите кнопку “New +” и выберите “PostgreSQL”.

Name: Укажите имя для вашей базы данных.

Database Name: MOSH

User: postgres
Password: rootroot1!
Region: Russia
Plan: Выберите тарифный план: Free

Получите строку подключения к базе данных:
После создания базы данных Render предоставит строку подключения (Connection String). Она будет выглядеть примерно так: postgres://<user>:<password>@<host>:<port>/<database>. Скопируйте эту строку.