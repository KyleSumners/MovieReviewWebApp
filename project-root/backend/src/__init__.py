# This file allows Python to treat the directory as a package
# It also initializes the database when the application starts

from src.database import init_db

# Initialize database tables
try:
    init_db()
except Exception as e:
    print(f"Failed to initialize database: {e}") 