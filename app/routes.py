from sanic import Blueprint, response
from sanic_jwt import protected, inject_user

from sqlalchemy.future import select

from app.models import User, Account, Transaction
from app.utils import verify_signature, hash_password

# Создание экземпляра Blueprint для маршрутов
bp = Blueprint('main')


# Маршрут для получения данных о пользователе
@bp.route('/user/<user_id:int>', methods=['GET'])
@protected()
@inject_user()
async def get_user(request, user, user_id):
    # Проверка прав доступа пользователя
    if user_id != user['user_id'] and not user.get('is_admin'):
        return response.json({'error': 'Unauthorized'}, status=403)
    # Получение данных о пользователе из базы данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user_data = result.scalar()
        if user_data:
            return response.json({'id': user_data.id, 'email': user_data.email, 'full_name': user_data.full_name})
        return response.json({'error': 'User not found'}, status=404)


# Маршрут для получения списка счетов пользователя
@bp.route('/user/<user_id:int>/accounts', methods=['GET'])
@protected()
@inject_user()
async def get_user_accounts(request, user, user_id):
    # Проверка прав доступа пользователя
    if user_id != user['user_id'] and not user.get('is_admin'):
        return response.json({'error': 'Unauthorized'}, status=403)
    # Получение списка счетов пользователя из базы данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(Account).filter_by(user_id=user_id))
        accounts = result.scalars().all()
        return response.json([{'id': account.id, 'balance': account.balance} for account in accounts])


# Маршрут для получения списка платежей пользователя
@bp.route('/user/<user_id:int>/transactions', methods=['GET'])
@protected()
@inject_user()
async def get_user_transactions(request, user, user_id):
    # Проверка прав доступа пользователя
    if user_id != user['user_id'] and not user.get('is_admin'):
        return response.json({'error': 'Unauthorized'}, status=403)
    # Получение списка платежей пользователя из базы данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(Transaction).filter_by(user_id=user_id))
        transactions = result.scalars().all()
        return response.json([{'transaction_id': tx.transaction_id, 'amount': tx.amount} for tx in transactions])


# Маршрут для получения списка всех пользователей (доступен только администраторам)
@bp.route('/admin/users', methods=['GET'])
@protected()
async def get_users(request):
    # Получение списка пользователей из базы данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return response.json([{'id': user.id, 'email': user.email, 'full_name': user.full_name} for user in users])


# Маршрут для создания нового пользователя (доступен только администраторам)
@bp.route('/admin/user', methods=['POST'])
@protected()
async def create_user(request):
    data = request.json
    # Создание нового пользователя
    async with request.app.ctx.db() as session:
        user = User(email=data['email'], full_name=data.get('full_name'))
        user.password = hash_password(data['password'])
        user.is_admin = data.get('is_admin', 0)
        session.add(user)
        await session.commit()
        return response.json({'id': user.id, 'email': user.email, 'full_name': user.full_name})


# Маршрут для удаления пользователя (доступен только администраторам)
@bp.route('/admin/user/<user_id:int>', methods=['DELETE'])
@protected()
async def delete_user(request, user_id):
    # Удаление пользователя из базы данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar()
        if user:
            await session.delete(user)
            await session.commit()
            return response.json({'status': 'deleted'})
        return response.json({'error': 'User not found'}, status=404)


# Маршрут для обновления данных пользователя (доступен только администраторам)
@bp.route('/admin/user/<user_id:int>', methods=['PUT'])
@protected()
async def update_user(request, user_id):
    data = request.json
    # Обновление данных пользователя
    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            return response.json({"error": "User not found"}, status=404)

        user.email = data.get("email", user.email)
        user.full_name = data.get("full_name", user.full_name)
        if "password" in data:
            user.password = hash_password(data["password"])

        await session.commit()
        return response.json({"id": user.id, "email": user.email, "full_name": user.full_name})


# Маршрут для обработки вебхуков от платежной системы
@bp.route('/webhook', methods=['POST'])
async def handle_webhook(request):
    data = request.json
    signature = data.pop('signature')
    # Проверка подписи вебхука
    if not verify_signature(data, signature):
        return response.json({'error': 'Invalid signature'}, status=400)

    async with request.app.ctx.db() as session:
        # Проверка существования транзакции
        result = await session.execute(select(Transaction).filter_by(transaction_id=data['transaction_id']))
        transaction = result.scalar()
        if transaction:
            return response.json({'error': 'Transaction already exists'}, status=400)

        # Проверка и создание счета пользователя
        result = await session.execute(select(Account).filter_by(id=data['account_id'], user_id=data['user_id']))
        account = result.scalar()
        if not account:
            account = Account(id=data['account_id'], user_id=data['user_id'], balance=0)
            session.add(account)
            await session.commit()

        # Создание новой транзакции и обновление баланса счета
        transaction = Transaction(transaction_id=data['transaction_id'], amount=data['amount'], account_id=account.id,
                                  user_id=account.user_id)
        session.add(transaction)
        account.balance += data['amount']
        await session.commit()
        return response.json({'status': 'success'})
