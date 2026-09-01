from pathlib import Path
from unittest.mock import Mock, patch

from config import Config
from remarkable import RemarkableUploader


def test_upload_uses_folder_with_spaces_as_single_rmapi_argument():
    original_folder = Config.REMARKABLE_FOLDER
    Config.REMARKABLE_FOLDER = "NYT Crosswords"

    completed = Mock(returncode=0, stdout="", stderr="")

    try:
        with patch("remarkable.subprocess.run", return_value=completed) as run:
            uploader = RemarkableUploader()
            assert uploader.upload_pdf(Path("2026-08-23 Sunday NYT Crossword.pdf"))

        commands = [call.args[0] for call in run.call_args_list]
        assert ["rmapi", "mkdir", "NYT Crosswords"] in commands
        assert [
            "rmapi",
            "put",
            "2026-08-23 Sunday NYT Crossword.pdf",
            "NYT Crosswords",
        ] in commands
    finally:
        Config.REMARKABLE_FOLDER = original_folder
