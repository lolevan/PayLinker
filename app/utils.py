import hashlib
from passlib.hash import pbkdf2_sha256
from app.config import SECRET_KEY


# Функция для генерации цифровой подписи
def generate_signature(data):
    # Сортировка ключей словаря
    sorted_keys = sorted(data.keys())
    # Конкатенация значений ключей в алфавитном порядке и добавление секретного ключа
    concat_str = ''.join(str(data[key]) for key in sorted_keys) + SECRET_KEY
    # Генерация SHA256 хеша из конкатенированной строки
    return hashlib.sha256(concat_str.encode()).hexdigest()


# Функция для проверки цифровой подписи
def verify_signature(data, signature):
    # Сравнение сгенерированной подписи с предоставленной подписью
    return generate_signature(data) == signature


# Функция для хэширования пароля
def hash_password(password):
    # Использование pbkdf2_sha256 для хэширования пароля
    return pbkdf2_sha256.hash(password)


# Функция для проверки пароля
def verify_password(password, hashed_password):
    # Сравнение предоставленного пароля с хэшированным паролем
    return pbkdf2_sha256.verify(password, hashed_password)
