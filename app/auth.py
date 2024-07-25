from sanic import Sanic
from sanic_jwt import exceptions, initialize

from sqlalchemy.future import select

from app.utils import verify_password
from app.models import User


async def authenticate(request, *args, **kwargs):
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        raise exceptions.AuthenticationFailed("Email or password not provided.")

    async with request.app.db.session() as session:
        result = await session.execute(select(User).filter_by(email=email))
        user = result.scalar()

        if user and verify_password(password, user.password):
            return {'user_id': user.id, 'email': user.email, 'is_admin': user.is_admin}

        raise exceptions.AuthenticationFailed("Invalid email or password.")


def retrieve_user(request, payload, *args, **kwargs):
    user_id = payload.get('user_id')
    return {'user_id': user_id, 'email': payload.get('email'), 'is_admin': payload.get('is_admin')}


def extend_payload(payload, user, *args, **kwargs):
    payload.update({'email': user.get('email'), 'is_admin': user.get('is_admin')})
    return payload


def setup_jwt(app: Sanic):
    initialize(app, authenticate=authenticate, retrieve_user=retrieve_user, extend_payload=extend_payload)