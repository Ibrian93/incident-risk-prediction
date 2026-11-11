"""Acquire the source ZIP without transforming its contents."""
import shutil
import zipfile
from pathlib import Path

import requests

from config import SOURCE_ZIP_PATH, ZIP_PATH

DATA_URL = "https://www.osha.gov/sites/default/files/January2015toOctober2025.zip"


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        if not zipfile.is_zipfile(output_path):
            raise ValueError(f"Existing source is not a valid ZIP: {output_path}")
        print(f"Reusing source: {output_path}")
        return

    temporary_path = output_path.with_suffix(".zip.part")
    try:
        if SOURCE_ZIP_PATH.is_file():
            print(f"Importing source ZIP from {SOURCE_ZIP_PATH}")
            shutil.copyfile(SOURCE_ZIP_PATH, temporary_path)
        else:
            print(f"Downloading source from {url}")
            with requests.get(url, timeout=60, stream=True) as response:
                response.raise_for_status()
                with temporary_path.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        output.write(chunk)
        if not zipfile.is_zipfile(temporary_path):
            raise ValueError("Source response is not a valid ZIP.")
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    print(f"Saved source to {output_path}")


if __name__ == "__main__":
    download_file(DATA_URL, ZIP_PATH)
