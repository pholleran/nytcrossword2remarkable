from datetime import date

from config import Config


def test_puzzle_url_uses_three_character_english_month_names():
    examples = {
        date(2026, 1, 23): "Jan2326",
        date(2026, 2, 23): "Feb2326",
        date(2026, 3, 23): "Mar2326",
        date(2026, 4, 23): "Apr2326",
        date(2026, 5, 23): "May2326",
        date(2026, 6, 23): "Jun2326",
        date(2026, 7, 23): "Jul2326",
        date(2026, 8, 23): "Aug2326",
        date(2025, 9, 23): "Sep2325",
        date(2025, 10, 23): "Oct2325",
        date(2025, 11, 23): "Nov2325",
        date(2025, 12, 23): "Dec2325",
    }

    for puzzle_date, slug in examples.items():
        assert Config.get_puzzle_slug(puzzle_date) == slug
        assert Config.get_puzzle_url(puzzle_date).endswith(f"/{slug}.pdf")


def test_output_filename_sorts_by_date_and_includes_weekday():
    assert (
        Config.get_output_filename(date(2026, 8, 30))
        == "2026-08-30 Sunday NYT Crossword.pdf"
    )
