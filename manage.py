#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Run administrative tasks."""

    # === Cargar variables de entorno desde .env ===
    BASE_DIR = Path(__file__).resolve().parent
    dotenv_path = BASE_DIR / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ia_assistant.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
