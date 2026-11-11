# 가이드

- [가이드](#가이드)
  - [편집기에서 실행 방법](#편집기에서-실행-방법)
    - [구글 플레이 창은 항상 전체화면 f11](#구글-플레이-창은-항상-전체화면-f11)
  - [exe 파일로 만드는 방법](#exe-파일로-만드는-방법)
    - [exe 파일과 macro.py, .env 파일은 같은 폴더에 있어야 합니다](#exe-파일과-macropy-env-파일은-같은-폴더에-있어야-합니다)
  - [macro 수정 방법](#macro-수정-방법)

## 편집기에서 실행 방법

### 구글 플레이 창은 항상 전체화면 f11

폴더 위치 agent에서 아래 명령어를 cmd에서 실행

``` bat
cd agent
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
.\.venv\Scripts\Python.exe agent.py
```

## exe 파일로 만드는 방법

### exe 파일과 macro.py, .env 파일은 같은 폴더에 있어야 합니다

폴더 위치 agent에서 아래 명령어 cmd에서 실행
실행 후 dist 폴더에 exe 파일 생성

``` bat
pyinstaller --clean --onefile --console --name agent --icon "favicon.ico" --collect-all rapidocr --add-data "image_match/templates;image_match/templates" agent.py
```

## macro 수정 방법

macro.py에 구글 플레이 게임즈 for pc에서 f11 전체화면 기준으로 작성된 버튼별 위치가 _pos에 저장되어 있습니다.

해당 위치를 기준으로 각 시퀀스가 _sequence에 저장되어 있습니다.

_sequence가 모여서 macros가 됩니다. 이 단계부터 client에서 실행이 가능합니다.

만약 더 복잡한 매크로를 위한다면 multi_macros 변수가 있습니다. 이는 조건, 종료 시 처리 등등 복잡한 기능을 제공하며
여러 매크로를 합칠 수 있습니다.

해당 파일은 매크로 실행 시마다 읽기 때문에 수정사항이 즉시 반영됩니다.
