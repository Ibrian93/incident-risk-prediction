from pathlib import Path
import requests

DATA_URL = "https://www.osha.gov/sites/default/files/January2015toOctober2025.zip"


RAW_DIR = Path("data/raw")
ZIP_PATH = RAW_DIR / "osha_severe_injuries.zip"

def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return

    print(f"Downloading data from {url}")
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    print(f"Saved file to {output_path}")


if __name__ == "__main__":
    download_file(DATA_URL, ZIP_PATH)
