import logging
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
    logging.info("No data to seed, skipping...")