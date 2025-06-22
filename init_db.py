from app.database import Base, engine, SessionLocal
from app.models import User, Cedula
from app.auth import get_password_hash

def init_db():
    # Create all tables
    # Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Create admin user if not exists
        if not db.query(User).filter(User.username == "admin").first():
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()

        # Create regular user if not exists
        if not db.query(User).filter(User.username == "user").first():
            regular_user = User(
                username="user",
                hashed_password=get_password_hash("user123"),
                is_admin=False
            )
            db.add(regular_user)
            db.commit()

        # Add some sample cedulas if none exist
        if not db.query(Cedula).first():
            cedulas = [
                Cedula(cedula_number="1234567890"),
                Cedula(cedula_number="0987654321"),
                Cedula(cedula_number="1122334455")
            ]
            db.add_all(cedulas)
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")