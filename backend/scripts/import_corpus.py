"""
Standalone script to ingest a corpus JSON file (matching the documented format)
directly into the database.

Usage:
    python scripts/import_corpus.py corpus/data/dictations.json [limit]
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.memory_service import get_or_create_user, ingest_dictation, apply_decay


def main(path: str, limit: int = None):
    with open(path) as f:
        data = json.load(f)

    records = data["records"][:limit] if limit else data["records"]

    db = SessionLocal()
    user = get_or_create_user(db, data["user_name"])
    print(f"Ingesting {len(records)} records for user '{data['user_name']}' (id={user.id})")

    start = time.time()
    skipped = 0
    for i, record in enumerate(records, 1):
        result = ingest_dictation(db, user, record)
        if result.get("skipped"):
            skipped += 1
        if i % 25 == 0 or i == len(records):
            elapsed = time.time() - start
            print(f"  [{i}/{len(records)}] elapsed={elapsed:.1f}s skipped={skipped}")

    decayed = apply_decay(db, user.id)
    print(f"Done. Skipped {skipped} already-ingested. Decayed {decayed} episodic memories.")
    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_corpus.py <path_to_corpus.json> [limit]")
        sys.exit(1)
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(sys.argv[1], lim)