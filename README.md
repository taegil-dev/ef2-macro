# Google Play Games for PC Macro

- [Google Play Games for PC Macro](#google-play-games-for-pc-macro)
  - [실행 방법](#실행-방법)
    - [요구사항](#요구사항)
    - [편집기에서 실행](#편집기에서-실행)
    - [빌드](#빌드)
    - [dist 폴더에 생긴 exe 파일 agent 폴더로 이동](#dist-폴더에-생긴-exe-파일-agent-폴더로-이동)
  - [매크로 에디터](#매크로-에디터)
    - [구조](#구조)

## 실행 방법

### 요구사항

- above Python 3.6
- F11 maximizing on Google Play Games for PC

### 편집기에서 실행

``` bat
cd agent
python -m venv .venv
.\.venv\Scripts\activate.bat
.\.venv\Scripts\Python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Python.exe agent.py
```

(작업 디렉토리가 이미 agent라면 cd agent는 무시)

### 빌드

``` bat
cd agent
.\.venv\Scripts\python.exe -m PyInstaller --clean --onefile --console --name agent --icon "favicon.ico" --collect-all rapidocr --add-data "templates;templates" agent.py
pyinstaller --clean --onefile --console --name updater ./updater/updater.py
```

(작업 디렉토리가 이미 agent라면 cd agent는 무시)

### dist 폴더에 생긴 exe 파일 agent 폴더로 이동

``` bat
agent/
├── dist/
│   ├── agent.exe
│   └── updater.exe
├── .env
├── macro.py
└── version.json
```

## 매크로 에디터

### 구조

- macro.py
  - multi_macros
    - macros
      - sequence
        - pos
        - delay
  - screen_regions

macro.py에 구글 플레이 게임즈 for pc에서 f11 전체화면 기준으로 작성된 버튼별 위치가 _pos에 저장되어 있습니다.

해당 위치를 기준으로 각 시퀀스가 _sequence에 저장되어 있습니다.

_sequence가 모여서 macros가 됩니다. 이 단계부터 client에서 실행이 가능합니다.

만약 더 복잡한 매크로를 위한다면 multi_macros 변수가 있습니다. 이는 조건, 종료 시 처리 등등 복잡한 기능을 제공하며
여러 매크로를 합칠 수 있습니다.

해당 파일은 매크로 실행 시마다 읽기 때문에 수정사항이 즉시 반영됩니다.
