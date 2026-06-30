"""
Migration script. Creates all tables and seeds initial data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine, SessionLocal, Base
from models.user import User, UserRole
from models.instrument import Instrument, InstrumentStatus
from models.movement import Movement
from models.calibration import Calibration
from core.security import hash_password
from datetime import datetime
import uuid


def run_migrations():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")


def seed_users():
    db = SessionLocal()
    if db.query(User).count() == 0:
        users = [
            User(badge_number="ADMIN-001", full_name="Ivanov I.I.", workshop="Workshop 1", role=UserRole.ADMIN, hashed_password=hash_password("admin123")),
            User(badge_number="METRO-001", full_name="Petrov P.P.", workshop="Laboratory", role=UserRole.METROLOGIST, hashed_password=hash_password("metro123")),
            User(badge_number="W-5432", full_name="Sidorov S.S.", workshop="Workshop 3", role=UserRole.WORKER, hashed_password=hash_password("worker123")),
        ]
        db.add_all(users)
        db.commit()
        print("Users created!")
    else:
        print("Users already exist.")
    db.close()


def seed_instruments():
    db = SessionLocal()
    if db.query(Instrument).count() == 0:
        instruments = [
            Instrument(barcode=f"BELAZ-{uuid.uuid4().hex[:8].upper()}", name="Torque wrench 50Nm", model="TORCOFIX 50", serial_number="SN-001", workshop="Workshop 3", status=InstrumentStatus.AVAILABLE, next_verification_date=datetime(2027, 6, 25)),
            Instrument(barcode=f"BELAZ-{uuid.uuid4().hex[:8].upper()}", name="Torque wrench 200Nm", model="TORCOFIX 200", serial_number="SN-002", workshop="Workshop 3", status=InstrumentStatus.EXPIRED, next_verification_date=datetime(2025, 1, 1)),
            Instrument(barcode=f"BELAZ-{uuid.uuid4().hex[:8].upper()}", name="Laser tracker", model="Leica AT960", serial_number="LT-001", workshop="Workshop 7", status=InstrumentStatus.EXPIRED, next_verification_date=datetime(2024, 6, 1)),
            Instrument(barcode=f"BELAZ-{uuid.uuid4().hex[:8].upper()}", name="Digital micrometer", model="Mitutoyo 0-25", serial_number="MM-001", workshop="Workshop 1", status=InstrumentStatus.AVAILABLE, next_verification_date=datetime(2027, 12, 31)),
            Instrument(barcode=f"BELAZ-{uuid.uuid4().hex[:8].upper()}", name="Caliper", model="SCC-I 150", serial_number="SC-001", workshop="Workshop 5", status=InstrumentStatus.AVAILABLE, next_verification_date=datetime(2026, 7, 15)),
        ]
        db.add_all(instruments)
        db.commit()
        print("Instruments created!")
    else:
        print("Instruments already exist.")
    db.close()


if __name__ == "__main__":
    run_migrations()
    seed_users()
    seed_instruments()
    print("Done!")