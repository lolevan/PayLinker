import os


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@db/myapp')
SECRET_KEY = os.getenv('SECRET_KEY', 'gfdmhghif38yrf9ew0jkf32')
JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_key')
