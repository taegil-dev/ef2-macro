# Google Play Games for PC Macro

- [Google Play Games for PC Macro](#google-play-games-for-pc-macro)
  - [지원하는 게임](#지원하는-게임)
  - [실행 방법](#실행-방법)
    - [요구사항](#요구사항)
    - [편집기에서 실행](#편집기에서-실행)
    - [빌드](#빌드)
    - [dist 폴더에 생긴 exe 파일 agent 폴더로 이동](#dist-폴더에-생긴-exe-파일-agent-폴더로-이동)
  - [매크로 에디터](#매크로-에디터)

## 지원하는 게임

- Endless Frontier 2

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
