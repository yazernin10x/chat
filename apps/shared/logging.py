import sys
from pathlib import Path

from loguru import logger

# Obtenir le chemin du dossier logs
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configuration de base
config = {
    "handlers": [
        # Handler pour la console
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": "INFO",
        },
        # Handler pour les logs généraux
        {
            "sink": LOGS_DIR / "app.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "rotation": "1 day",
            "retention": "1 month",
            "compression": "zip",
            "level": "INFO",
        },
        # Handler pour les erreurs
        {
            "sink": LOGS_DIR / "errors.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
            "rotation": "1 day",
            "retention": "1 month",
            "compression": "zip",
            "level": "ERROR",
        },
    ],
}

# Configuration de loguru
for handler in config["handlers"]:
    logger.add(**handler)


# Fonction pour obtenir un logger personnalisé
def get_logger(name: str):
    return logger.bind(name=name)


# Gestion des exceptions non gérées
def log_exceptions(exc_type, exc_value, tb):
    logger.exception(
        "Une exception non gérée a été levée", exc_info=(exc_type, exc_value, tb)
    )
    raise exc_type(exc_value)


sys.excepthook = log_exceptions
