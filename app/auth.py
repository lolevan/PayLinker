from sanic import Sanic
from sanic_jwt import exceptions, initialize

from sqlalchemy.future import select

from app.utils import verify_password
from app.models import User
from app.config import JWT_SECRET


# Функция аутентификации пользователя
async def authenticate(request, *args, **kwargs):
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    # Проверка наличия email и пароля в запросе
    if not email or not password:
        raise exceptions.AuthenticationFailed("Email or password not provided.")

    # Проверка email и пароля пользователя в базе данных
    async with request.app.ctx.db() as session:
        result = await session.execute(select(User).filter_by(email=email))
        user = result.scalar()

        # Если пользователь найден и пароль совпадает
        if user and verify_password(password, user.password):
            return {'user_id': user.id, 'email': user.email, 'is_admin': user.is_admin}

        # Исключение при неудачной аутентификации
        raise exceptions.AuthenticationFailed("Invalid email or password.")


# Функция получения пользователя по данным JWT
def retrieve_user(request, payload, *args, **kwargs):
    user_id = payload.get('user_id')
    return {'user_id': user_id, 'email': payload.get('email'), 'is_admin': payload.get('is_admin')}


# Функция расширения полезной нагрузки JWT
def extend_payload(payload, user, *args, **kwargs):
    payload.update({'email': user.get('email'), 'is_admin': user.get('is_admin')})
    return payload


# Настройка JWT аутентификации для приложения Sanic
def setup_jwt(app: Sanic):
    initialize(app, authenticate=authenticate, retrieve_user=retrieve_user, extend_payload=extend_payload,
               secret=JWT_SECRET)
