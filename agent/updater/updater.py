import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import httpx
import psutil

BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent

exclude_files = ["updater.exe", "release.zip"]


def move_folder_files(src_folder: Path, dest_folder: Path):
    dest_folder.mkdir(exist_ok=True)

    for file in src_folder.iterdir():
        if file.name in exclude_files:
            continue

        os.replace(
            src_folder / file.name, 
            dest_folder / file.name)


def main():
    pid = int(sys.argv[1])
    assets = json.loads(sys.argv[2])

    # 기존 Agent 종료 대기
    proc = None
    try:
        proc = psutil.Process(pid)
        proc.wait(timeout=30)
    except psutil.NoSuchProcess:
        pass
    except psutil.TimeoutExpired:
        print("대기 시간 초과")
        return
    
    if proc and proc.is_running():
        print("agent.exe 종료 실패; 업데이트 실패")
        return

    temp_folder = BASE_DIR / "temp"
    temp_folder.mkdir(exist_ok=True)

    print()
    for asset in assets["assets"]:
        with httpx.stream(
            "GET", 
            asset["url"], 
            follow_redirects=True, 
            timeout=30) as response:

            response.raise_for_status()

            total_size = int(asset["size"] or 0)
            downloaded = 0
            with open(temp_folder / asset["filename"], "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        progress = min(downloaded / total_size, 1.0)
                        bar_length = 30
                        filled = int(bar_length * progress)

                        bar = "█" * filled + "░" * (bar_length - filled)

                        print(
                            f"\r[{bar}] {progress * 100:5.1f}% "
                            f"({downloaded / 1024 / 1024:.1f} / "
                            f"{total_size / 1024 / 1024:.1f} MB)",
                            end="",
                            flush=True
                        )
            print()

    with zipfile.ZipFile(temp_folder / "release.zip", "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    for file in temp_folder.iterdir():
        print(f"Moving {file.name} to {BASE_DIR}")
        if file.name in exclude_files:
            continue

        if file.is_dir():
            move_folder_files(file, BASE_DIR / file.name)
            continue

        os.replace(
            temp_folder / file.name, 
            BASE_DIR / file.name)

    shutil.rmtree(temp_folder)

    agent = os.path.join(BASE_DIR, "agent.exe")
    subprocess.Popen([agent], cwd=BASE_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)

    sys.exit(0)


if __name__ == "__main__":
    main()