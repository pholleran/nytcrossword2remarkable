# nytcrossword2remarkable

A GitHub Actions workflow that downloads the NYT Crossword as a PDF and uploads it into your reMarkable cloud account. Put your schedule and secret in a separate private repo, then call this action from that workflow.

## Use it from another repo

1. Create a private repository for your personal automation.
2. Add a repository secret named `DEVICE_TOKEN`.
3. Add this workflow:

```yaml
name: Download NYT crossword

on:
  schedule:
    - cron: "0 11 * * *" # 7 AM Eastern during daylight saving time
  workflow_dispatch:
    inputs:
      puzzle_date:
        description: "Puzzle date to download in YYYY-MM-DD format"
        required: false
        default: ""
        type: string

jobs:
  upload-crossword:
    runs-on: ubuntu-latest
    steps:
      - uses: pholleran/nytcrossword2remarkable@main
        with:
          device_token: ${{ secrets.DEVICE_TOKEN }}
          puzzle_date: ${{ github.event_name == 'workflow_dispatch' && inputs.puzzle_date || '' }}
          remarkable_folder: "NYT Crosswords"
```

When `puzzle_date` is blank, the action downloads today’s puzzle using the `America/New_York` date.

## Get a reMarkable device token

Authenticate with [`rmapi`](https://github.com/ddvk/rmapi) once, then print the token:

```bash
brew install rmapi
rmapi

git clone https://github.com/pholleran/nytcrossword2remarkable.git
cd nytcrossword2remarkable
./TOKEN_RETRIEVER.sh
```

Copy the printed value into the caller repo’s `DEVICE_TOKEN` Actions secret.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `device_token` | Yes |  | reMarkable device token from `rmapi` |
| `puzzle_date` | No | Today in New York | Puzzle date in `YYYY-MM-DD` format |
| `remarkable_folder` | No | `NYT Crosswords` | Destination folder in reMarkable Cloud |
| `rmapi_timeout` | No | `120` | Seconds to wait for each `rmapi` command |

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Download and upload a specific puzzle:

```bash
python main.py \
  --puzzle-date 2026-08-23 \
  --remarkable-folder "NYT Crosswords"
```

Download without uploading:

```bash
python main.py --puzzle-date 2026-08-23 --no-upload
```

## How puzzle URLs are built

NYT crossword PDFs use a three-letter English month abbreviation, two-digit day, and two-digit year:

```text
https://www.nytimes.com/svc/crosswords/v2/puzzle/print/Aug2326.pdf
```

For `2026-08-23`, this action downloads `Aug2326.pdf` and uploads it as:

```text
2026-08-23 Sunday NYT Crossword.pdf
```
