import os
from pathlib import Path
import sys
import zipfile

import httpx
import psutil

import check_update as cu

BASE_DIR = getattr(sys, "frozen", False) and Path(sys.executable).resolve().parent or Path(__file__).resolve().parent.parent
REPO = "taegil-dev/ef2-macro"

def main():
    cu.check_update()
    if cu._update_data is None:
        print("❌ 설치 가능한 버전이 없습니다.")
        return
    
    # pid = int(sys.argv[1])
    
    # # 기존 Agent 종료 대기
    # try:
    #     proc = psutil.Process(pid)
    #     proc.wait(timeout=30)
    # except psutil.NoSuchProcess:
    #     pass
    # except psutil.TimeoutExpired:
    #     print("대기 시간 초과")
    #     return

    temp_folder = BASE_DIR / "temp"
    temp_folder.mkdir(exist_ok=True)

    for asset in cu._update_data["assets"]:
        with httpx.stream(
            "GET", 
            asset["url"], 
            follow_redirects=True, 
            timeout=30) as response:

            response.raise_for_status()
            
            with open(temp_folder / asset["filename"], "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    with zipfile.ZipFile("update.zip", "r") as zip_ref:
        zip_ref.extractall("./updates")

    # for asset in cu._update_data["assets"]:
    #     os.replace(
    #         temp_folder / asset["filename"], 
    #         BASE_DIR / asset["filename"])

    # os.startfile(BASE_DIR / "agent.exe")

if __name__ == "__main__":
    main()