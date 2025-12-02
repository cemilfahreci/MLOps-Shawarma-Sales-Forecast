import asyncio
import sys
import os
import glob
from pathlib import Path
import shutil
from sqlalchemy import text

# Add backend directory to python path
backend_dir = Path(__file__).resolve().parent / "app"
sys.path.append(str(backend_dir.parent))

from app.database import AsyncSessionLocal

async def hard_reset():
    print("WARNING: Initiating Hard Reset...")
    
    # 1. Database Reset
    print("1. Truncating Database Tables...")
    async with AsyncSessionLocal() as session:
        try:
            # Use CASCADE to handle foreign keys if any, and RESTART IDENTITY to reset IDs
            await session.execute(text("TRUNCATE TABLE sales RESTART IDENTITY CASCADE"))
            await session.execute(text("TRUNCATE TABLE model_versions RESTART IDENTITY CASCADE"))
            await session.commit()
            print("   > Database cleared.")
        except Exception as e:
            print(f"   > Error clearing DB: {e}")
        finally:
            await session.close()

    # 2. Delete Model Files
    print("2. Deleting Model Artifacts (.pkl)...")
    model_dir = backend_dir / "ml" / "models"
    files = glob.glob(str(model_dir / "*.pkl"))
    for f in files:
        try:
            os.remove(f)
            print(f"   > Deleted: {Path(f).name}")
        except Exception as e:
            print(f"   > Error deleting {f}: {e}")

    # 3. Delete MLflow Data
    print("3. Deleting MLflow Data (mlruns)...")
    mlruns_dir = backend_dir.parent / "mlruns"
    if mlruns_dir.exists():
        try:
            shutil.rmtree(mlruns_dir)
            print("   > Deleted mlruns directory.")
        except Exception as e:
            print(f"   > Error deleting mlruns: {e}")

    # 4. Skip Deleting Generated Data (Preserve for user)
    print("4. Skipping Data Deletion (Preserved in /Desktop/veriler)...")

    print("\nSUCCESS: Project reset to ZERO state.")

if __name__ == "__main__":
    asyncio.run(hard_reset())
