import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.world.seed import load_definitions, seed_world


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    with SessionLocal() as session:
        seed_world(session, load_definitions(root / "data" / "world.json"))
    print("Football World seeded successfully.")
