"""Connects to Firestore with the Firebase Admin SDK.

Credentials are loaded from, in order:
1. A [firebase_service_account] table in .streamlit/secrets.toml (best for cloud hosting), or
2. serviceAccountKey.json in the project folder (easiest locally).

Neither is ever printed or logged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.config import BASE_DIR
from core.repository import EcoRepository

DEFAULT_KEY_FILE = BASE_DIR / "serviceAccountKey.json"


class FirebaseSetupError(RuntimeError):
    """Raised with a user-friendly explanation when Firebase can't be reached."""


def create_repository(service_account: Mapping[str, Any] | None = None,
                      key_file: Path = DEFAULT_KEY_FILE) -> EcoRepository:
    try:
        import firebase_admin
        from firebase_admin import credentials
        from firebase_admin import firestore as admin_firestore
        from google.cloud import firestore as fs
    except ImportError as exc:  # pragma: no cover - depends on installation
        raise FirebaseSetupError(
            "firebase-admin is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    try:
        app = firebase_admin.get_app()
    except ValueError:
        if service_account:
            cred = credentials.Certificate(dict(service_account))
        elif key_file.is_file():
            cred = credentials.Certificate(str(key_file))
        else:
            raise FirebaseSetupError(
                "Firebase credentials not found. Put serviceAccountKey.json in the "
                "project folder (next to app.py), or add a [firebase_service_account] "
                "section to .streamlit/secrets.toml."
            )
        try:
            app = firebase_admin.initialize_app(cred)
        except Exception as exc:
            raise FirebaseSetupError(
                "The Firebase service account file could not be read. Download a fresh key "
                "from Firebase Console > Project settings > Service accounts."
            ) from exc

    return EcoRepository(admin_firestore.client(app), fs)
