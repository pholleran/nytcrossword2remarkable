import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests

from config import Config
from remarkable import RemarkableUploader


class NYTCrosswordProcessor:
    def __init__(self, upload: bool = True) -> None:
        Config.setup_directories()
        self.upload = upload
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("NYTCrossword")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt=Config.LOG_DATE_FORMAT,
        )

        log_file = Config.LOG_DIR / f"nyt_crossword_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def download_pdf(self) -> Path:
        puzzle_date = Config.resolve_puzzle_date()
        url = Config.get_puzzle_url(puzzle_date)
        output_path = Config.OUTPUT_DIR / Config.get_output_filename(puzzle_date)

        if output_path.exists() and output_path.stat().st_size > 0:
            self.logger.info("PDF already exists locally: %s", output_path)
            return output_path

        self.logger.info("Downloading NYT crossword for %s from %s", puzzle_date.isoformat(), url)
        response = requests.get(
            url,
            headers={
                "Accept": "application/pdf",
                "User-Agent": Config.USER_AGENT,
            },
            timeout=Config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "application/pdf" not in content_type.lower() and not response.content.startswith(b"%PDF"):
            raise ValueError(f"Unexpected response content type: {content_type}")

        with NamedTemporaryFile(
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(response.content)

        temp_path.replace(output_path)
        self.logger.info("Downloaded PDF: %s", output_path)
        return output_path

    def run(self) -> int:
        pdf_path = self.download_pdf()

        if not self.upload:
            self.logger.info("Upload disabled; leaving PDF at %s", pdf_path)
            return 0

        uploader = RemarkableUploader()
        if uploader.upload_pdf(pdf_path):
            return 0

        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download the daily NYT crossword PDF and upload it to reMarkable Cloud"
    )
    parser.add_argument(
        "--puzzle-date",
        help="Puzzle date to download in YYYY-MM-DD format; defaults to today in America/New_York",
    )
    parser.add_argument("--output-dir", help="Directory for downloaded PDFs")
    parser.add_argument(
        "--remarkable-folder",
        help="Folder name in reMarkable Cloud for uploaded PDFs",
    )
    parser.add_argument("--rmapi-path", help="Path to rmapi binary")
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Download the PDF without uploading it to reMarkable Cloud",
    )

    args = parser.parse_args()

    if args.puzzle_date:
        Config.PUZZLE_DATE = args.puzzle_date
    if args.output_dir:
        Config.OUTPUT_DIR = Path(args.output_dir)
    if args.remarkable_folder:
        Config.REMARKABLE_FOLDER = args.remarkable_folder
    if args.rmapi_path:
        Config.RMAPI_PATH = args.rmapi_path

    try:
        Config.resolve_puzzle_date()
        processor = NYTCrosswordProcessor(upload=not args.no_upload)
        sys.exit(processor.run())
    except Exception as error:
        print(f"Application failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
