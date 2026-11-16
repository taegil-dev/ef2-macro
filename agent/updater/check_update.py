import json
import os
from pathlib import Path
import sys

import httpx
from packaging.version import Version


BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent
REPO = "taegil-dev/ef2-macro"


def get_current_version():
    path = os.path.join(BASE_DIR, "version.json")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["version"]


def check_update():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"

    with httpx.Client(timeout=10) as client:
        response = client.get(url)
        response.raise_for_status()

        release = response.json()

    latest_version = release["tag_name"].lstrip("v")
    current_version = get_current_version()

    if Version(latest_version) <= Version(current_version):
        return False, None

    assets = [{
        "url": asset["browser_download_url"], 
        "size": asset["size"], 
        "filename": asset["name"]
        } for asset in release["assets"]]
    
    update_data = {
        "version": latest_version,
        "assets": assets
    }

    return True, update_data
