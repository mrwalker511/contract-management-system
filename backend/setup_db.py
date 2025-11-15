#!/usr/bin/env python
"""
Database setup script - creates database and tables
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from app.core.database import Base, engine
from app.core.config import settings
from app.models.user import User
from app.models.contract import Contract
from app.models.template import Template

def setup_database():
    """Create database and tables"""
    
    # Try to create tables
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    try:
        print(f"Connecting to: {settings.DATABASE_URL}")
        if setup_database():
            print("\n✓ Database setup complete!")
            sys.exit(0)
        else:
            print("\n✗ Database setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        sys.exit(1)
