from pathlib import Path
import json
from pydantic import ValidationError
from infrastructure.db.db_context import db
from models.Client import Client
from models.Claim import Claim
from models.ClientClaim import ClientClaim
from models.ClientEntry import ClientEntry
from auth.hash import hash_password

def seed_db(app):
    with app.app_context():
        clients = _load_clients_from_json("auth/clients.json")
        if clients is None:
            return

        _clear_existing_auth_data()
        _seed_clients_and_claims(clients)
        print(f"✅ Seeded {len(clients)} clients.")

def _load_clients_from_json(path_str):
    path = Path(path_str)
    if not path.exists():
        print("⚠️ No clients.json found, skipping seeding.")
        return None

    try:
        data = json.loads(path.read_text())
        return [ClientEntry(**entry) for entry in data]
    except (json.JSONDecodeError, ValidationError) as e:
        print("❌ Invalid clients.json format:", e)
        return None

def _clear_existing_auth_data():
    db.session.query(ClientClaim).delete()
    db.session.query(Client).delete()
    db.session.query(Claim).delete()
    db.session.commit()

def _seed_clients_and_claims(clients):
    for entry in clients:
        claim_objs = []
        for name in entry.claims:
            claim = db.session.query(Claim).filter_by(name=name).first()
            if not claim:
                claim = Claim(name=name, description=name)
                db.session.add(claim)
            claim_objs.append(claim)

        client = Client(
            username=entry.username,
            secret=hash_password(entry.secret),
            claims=claim_objs,
        )
        db.session.add(client)

    db.session.commit()