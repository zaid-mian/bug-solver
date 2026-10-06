import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config_loader import get_database_url


def test_full_config():
    assert get_database_url({'host': 'localhost', 'port': 5432, 'user': 'admin'}) == 'postgres://admin@localhost:5432/db'

def test_default_port():
    assert get_database_url({'host': 'localhost'}) == 'postgres://root@localhost:5432/db'
