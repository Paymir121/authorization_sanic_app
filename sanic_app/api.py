import hashlib
from datetime import datetime, timedelta

from sanic import Sanic, response
from sanic.cookies import response
from sanic.response import text
from sanic import json
from sanic.log import logger
from connection import DBConnection
from models import User, Order, BankAccount

"""Пользователь должен иметь следующие возможности:
Авторизоваться по email/password
Получить данные о себе(id, email, full_name)
Получить список своих счетов и балансов
Получить список своих платежей

Администратор должен иметь следующие возможности:
Авторизоваться по email/password
Получить данные о себе (id, email, full_name)
Создать/Удалить/Обновить пользователя
Получить список пользователей и список его счетов с балансами

"""


app: Sanic = Sanic("TestApplication")
connection: DBConnection = DBConnection()
SECRET_KEY = "gfdmhghif38yrf9ew0jkf32"

def generate_jwt(user_id, jwt=None):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def generate_signature(data):
    sorted_keys = sorted(data.keys())
    sorted_values = ''.join(str(data[key]) for key in sorted_keys)
    string_to_hash = f"{sorted_values}{SECRET_KEY}"
    signature = hashlib.sha256(string_to_hash.encode()).hexdigest()
    return signature

@app.post("/authorization")
async def authorization(request):
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return json({"error": "Email and password are required"}, status=400)

    user = connection.session.query(User).filter_by(username=username, password=password).first()

    if user:
        token = generate_jwt(user.id)
        return json({"token": token}, status=200)
    else:
        return json({"error": "Invalid credentials"}, status=401)


@app.get("/me")
async def get_user(request, jwt=None):
    token = request.headers.get("Authorization")
    if not token:
        return response.json({"error": "Authorization header is required"}, status=401)

    if not token:
        return text("errorAuthorization header is required")

    try:
        payload = jwt.decode(token.split(" ")[1], "SECRET_KEY", algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return json({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return json({"error": "Invalid token"}, status=401)
    try:
        user = connection.session.query(User).filter_by(id=user_id).first()
    except Exception as e:
        return json({"error": str(e)}, status=500)

    if user:
        return json({"id": user.id, "email": user.email, "full_name": user.full_name}, status=200)
    else:
        return json({"error": "User not found"}, status=404)


@app.get("/users")
async def list_users(request, jwt=None):
    token = request.headers.get("Authorization")
    if not token:
        return response.json({"error": "Authorization header is required"}, status=401)

    if not token:
        return text("errorAuthorization header is required")

    try:
        payload = jwt.decode(token.split(" ")[1], "SECRET_KEY", algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return json({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return json({"error": "Invalid token"}, status=401)
    try:
        user = connection.session.query(User).filter_by(id=user_id).first()
    except Exception as e:
        return json({"error": str(e)}, status=500)
    if not user.is_admin:
        return json({"error": "User is not admin"}, status=403)
    try:
        user = connection.session.query(User).filter_by().all()
    except Exception as e:
        return json({"error": str(e)}, status=500)

    if user:
        return json(user, status=200)
    else:
        return json({"error": "Users not found"}, status=404)


@app.get('/webhook')
async def webhook(request):
    data: dict = request.json
    required_fields = ['transaction_id', 'account_id', 'user_id', 'amount', 'signature']
    if not data:
        return json({'error 400.1': 'Нет данных'}, status=400)
    if not all(field in data for field in required_fields):
        return json({'error 400.2': 'Недостаточно данных'}, status=400)
    transaction_id = data['transaction_id']
    account_id = data['account_id']
    user_id = data['user_id']
    amount = data['amount']
    signature = hashlib.sha256(f"{account_id}{amount}{transaction_id}{user_id}{SECRET_KEY}".encode()).hexdigest()
    if signature != data['signature']:
        logger.info(f'1: {signature}, 2: {data["signature"]}')
        return json({'error 403.1': 'Неверная подпись'}, status=403)

    create_transaction(transaction_id, account_id, user_id, amount, signature)
    return json({'status': 'успешно обработано'}, status=200)

def create_transaction(transaction_id, account_id, user_id, amount, signature):
    """
    При обработке вебхука необходимо:
    Проверить существует ли у пользователя такой счет - если нет, его необходимо создать.
    Сохранить транзакцию в базе данных.
    Начислить сумму транзакции на счет пользователя.
    """
    account = connection.session.query(BankAccount).filter_by(
        id = account_id,
        user_id = user_id
    ).first()
    if not account:
        account = BankAccount(
            id = transaction_id,
            user_id = user_id,
            balance = amount
        )
        connection.session.add(account)
    else:
        account.balance += amount
    transaction = Order(
        transaction_id = transaction_id,
        amount = amount,
        bank_account = account
    )
    connection.session.add(transaction)
    connection.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)