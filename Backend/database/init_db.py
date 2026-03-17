import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app
from Backend.models import db


with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database initialized successfully.")
