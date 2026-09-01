import logging
import subprocess
from pathlib import Path

from config import Config


class RemarkableUploader:
    MAX_RMAPI_ERROR_LENGTH = 2000

    def __init__(self) -> None:
        self.logger = logging.getLogger("NYTCrossword")
        self.rmapi_path = Config.RMAPI_PATH
        self.folder_name = Config.REMARKABLE_FOLDER.strip("/")
        if not self.folder_name:
            raise ValueError("reMarkable folder name cannot be empty")

    def format_rmapi_error(self, result: subprocess.CompletedProcess[str]) -> str:
        output = (result.stderr or result.stdout or "").strip()
        if len(output) <= self.MAX_RMAPI_ERROR_LENGTH:
            return output

        return f"{output[: self.MAX_RMAPI_ERROR_LENGTH]}... [truncated]"

    def check_rmapi_available(self) -> bool:
        try:
            result = subprocess.run(
                [self.rmapi_path, "version"],
                capture_output=True,
                text=True,
                timeout=Config.RMAPI_TIMEOUT,
                check=False,
            )
        except FileNotFoundError:
            self.logger.error("rmapi not found at path: %s", self.rmapi_path)
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("rmapi version check timed out")
            return False

        if result.returncode == 0:
            self.logger.info("rmapi available: %s", result.stdout.strip())
            return True

        self.logger.error("rmapi error: %s", self.format_rmapi_error(result))
        return False

    def ensure_folder_exists(self) -> bool:
        try:
            find_result = subprocess.run(
                [self.rmapi_path, "find", self.folder_name],
                capture_output=True,
                text=True,
                timeout=Config.RMAPI_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.logger.error("Folder lookup timed out")
            return False

        if find_result.returncode == 0 and find_result.stdout.strip():
            self.logger.info("Folder '%s' already exists", self.folder_name)
            return True

        self.logger.info("Creating folder '%s' in reMarkable Cloud", self.folder_name)
        try:
            mkdir_result = subprocess.run(
                [self.rmapi_path, "mkdir", self.folder_name],
                capture_output=True,
                text=True,
                timeout=Config.RMAPI_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.logger.error("Folder creation timed out")
            return False

        if mkdir_result.returncode == 0:
            self.logger.info("Created folder '%s'", self.folder_name)
            return True

        if "already exists" in mkdir_result.stderr.lower():
            self.logger.info("Folder '%s' already exists", self.folder_name)
            return True

        self.logger.error("Failed to create folder: %s", self.format_rmapi_error(mkdir_result))
        return False

    def file_exists(self, pdf_path: Path) -> bool:
        remarkable_path = f"{self.folder_name}/{pdf_path.stem}"
        try:
            result = subprocess.run(
                [self.rmapi_path, "find", remarkable_path],
                capture_output=True,
                text=True,
                timeout=Config.RMAPI_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.logger.error("File lookup timed out for %s", pdf_path.name)
            return False

        return result.returncode == 0 and bool(result.stdout.strip())

    def upload_pdf(self, pdf_path: Path) -> bool:
        if not self.check_rmapi_available():
            return False

        if not self.ensure_folder_exists():
            return False

        if self.file_exists(pdf_path):
            self.logger.info("File already exists in reMarkable Cloud: %s", pdf_path.name)
            return True

        self.logger.info("Uploading %s to reMarkable folder: %s", pdf_path.name, self.folder_name)
        try:
            result = subprocess.run(
                [self.rmapi_path, "put", str(pdf_path), self.folder_name],
                capture_output=True,
                text=True,
                timeout=Config.RMAPI_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.logger.error("Upload timed out for %s", pdf_path.name)
            return False

        if result.returncode == 0:
            self.logger.info("Uploaded %s", pdf_path.name)
            return True

        self.logger.error("Failed to upload %s: %s", pdf_path.name, self.format_rmapi_error(result))
        return False
