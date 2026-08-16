from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = APP_ROOT
DATA_DIR = APP_ROOT / "data"
DB_ETICARET = DATA_DIR / "eticaret_analiz.db"
DB_SOHBET = DATA_DIR / "sohbet_gecmisi.db"
ENV_FILE = APP_ROOT / ".env"

SUPPORTED_LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
}
DEFAULT_LANGUAGE = "tr"
