import os
from datetime import timedelta

# Application settings
PEPPER = os.getenv('PEPPER', 'global-pepper-secret')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-jwt-secret-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'
