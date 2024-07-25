from sanic import Blueprint, response
from sanic_jwt import protected
from sqlalchemy.future import select
from app.models import User, Account, Transaction
from app.utils import verify_signature

bp = Blueprint('main')


@bp.route('/user/<user_id>', methods=['GET'])
@protected()
async def get_user(request, user_id):
    async with request.app.db.session() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar()
        if user:
            return response.json({'id': user.id, 'email': user.email, 'full_name': user.full_name})
        return response.json({'error': 'User not found'}, status=404)


@bp.route('/user/<user_id>/accounts', methods=['GET'])
@protected()
async def get_user_accounts(request, user_id):
    async with request.app.db.session() as session:
        result = await session.execute(select(Account).filter_by(user_id=user_id))
        accounts = result.scalars().all()
        return response.json([{'id': account.id, 'balance': account.balance} for account in accounts])


@bp.route('/user/<user_id>/transactions', methods=['GET'])
@protected()
async def get_user_transactions(request, user_id):
    async with request.app.db.session() as session:
        result = await session.execute(select(Transaction).filter_by(user_id=user_id))
        transactions = result.scalars().all()
        return response.json([{'transaction_id': tx.transaction_id, 'amount': tx.amount} for tx in transactions])


@bp.route('/admin/users', methods=['GET'])
@protected()
async def get_users(request):
    async with request.app.db.session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return response.json([{'id': user.id, 'email': user.email, 'full_name': user.full_name} for user in users])


@bp.route('/admin/user', methods=['POST'])
@protected()
async def create_user(request):
    data = request.json
    async with request.app.db.session() as session:
        user = User(email=data['email'], full_name=data.get('full_name'))
        user.set_password(data['password'])
        user.is_admin = data.get('is_admin', 0)
        session.add(user)
        await session.commit()
        return response.json({'id': user.id, 'email': user.email, 'full_name': user.full_name})


@bp.route('/admin/user/<user_id>', methods=['DELETE'])
@protected()
async def delete_user(request, user_id):
    async with request.app.db.session() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar()
        if user:
            await session.delete(user)
            await session.commit()
            return response.json({'status': 'deleted'})
        return response.json({'error': 'User not found'}, status=404)


@bp.route('/webhook', methods=['POST'])
async def handle_webhook(request):
    data = request.json
    signature = data.pop('signature')
    if not verify_signature(data, signature):
        return response.json({'error': 'Invalid signature'}, status=400)
    async with request.app.db.session() as session:
        result = await session.execute(select(Account).filter_by(id=data['account_id'], user_id=data['user_id']))
        account = result.scalar()
        if not account:
            account = Account(id=data['account_id'], user_id=data['user_id'], balance=0)
            session.add(account)
            await session.commit()
        transaction = Transaction(transaction_id=data['transaction_id'], amount=data['amount'], account_id=account.id, user_id=account.user_id)
        session.add(transaction)
        account.balance += data['amount']
        await session.commit()
        return response.json({'status': 'success'})
