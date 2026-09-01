import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class Config:
    MONTH_ABBREVIATIONS = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )

    APP_ROOT = Path(os.getenv("APP_ROOT", Path(__file__).resolve().parent))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", APP_ROOT / "output"))
    LOG_DIR = Path(os.getenv("LOG_DIR", APP_ROOT / "logs"))

    PUZZLE_DATE = os.getenv("PUZZLE_DATE", "")
    TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RMAPI_TIMEOUT = int(os.getenv("RMAPI_TIMEOUT", "120"))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "nytcrossword2remarkable/1.0 (+https://github.com/pholleran/nytcrossword2remarkable)",
    )

    REMARKABLE_FOLDER = os.getenv("REMARKABLE_FOLDER", "NYT Crosswords")
    RMAPI_PATH = os.getenv("RMAPI_PATH", "rmapi")

    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def setup_directories() -> None:
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        Config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def resolve_puzzle_date() -> date:
        if Config.PUZZLE_DATE:
            return datetime.strptime(Config.PUZZLE_DATE, "%Y-%m-%d").date()

        return datetime.now(ZoneInfo(Config.TIMEZONE)).date()

    @staticmethod
    def get_puzzle_slug(puzzle_date: date) -> str:
        month = Config.MONTH_ABBREVIATIONS[puzzle_date.month - 1]
        return f"{month}{puzzle_date.day:02d}{puzzle_date:%y}"

    @staticmethod
    def get_puzzle_url(puzzle_date: date) -> str:
        slug = Config.get_puzzle_slug(puzzle_date)
        return f"https://www.nytimes.com/svc/crosswords/v2/puzzle/print/{slug}.pdf"

    @staticmethod
    def get_output_filename(puzzle_date: date) -> str:
        weekday = puzzle_date.strftime("%A")
        return f"{puzzle_date.isoformat()} {weekday} NYT Crossword.pdf"
