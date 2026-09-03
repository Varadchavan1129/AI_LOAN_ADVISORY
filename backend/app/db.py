from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./loan_ai.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def ensure_db_schema_migrated():
    """
    Safely ensures SQLite tables have all new Phase 1 columns
    without dropping existing data.
    """
    with engine.connect() as conn:
        try:
            # Check existing columns in loan_applications
            res = conn.execute(text("PRAGMA table_info(loan_applications);")).fetchall()
            existing_cols = {row[1] for row in res}
            
            if existing_cols:
                # Column definitions to add if missing
                cols_to_add = [
                    ("employment_type", "TEXT DEFAULT 'salaried'"),
                    ("age", "INTEGER DEFAULT 30"),
                    ("credit_score", "INTEGER DEFAULT 750"),
                    ("loan_purpose", "TEXT DEFAULT 'personal'"),
                    ("estimated_emi", "REAL"),
                    ("foir_percentage", "REAL"),
                    ("max_eligible_loan", "REAL"),
                    ("risk_probability", "REAL"),
                    ("reason", "TEXT"),
                    ("assessment_snapshot", "TEXT"),
                ]
                
                for col_name, col_type in cols_to_add:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE loan_applications ADD COLUMN {col_name} {col_type};"))
                conn.commit()
        except Exception as e:
            print(f"DB migration notice: {e}")


ensure_db_schema_migrated()
