import sys
from sqlalchemy import inspect
from database.database import Base, engine 
from database.models import Course, Module, Section, Exercise, User, Completion

def create_tables():
    """Create all tables defined in models."""
    print("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def drop_tables():
    """Drop all tables in the database."""
    print("Dropping tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Remaining tables: {tables}")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        raise

def main(action: str):
    """Execute the specified database action."""
    if action == "create":
        create_tables()
    elif action == "reset":
        drop_tables()
    else:
        raise ValueError("Use 'create' or 'reset'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python db_helper.py [create|reset]")
        sys.exit(1)
    
    try:
        main(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

