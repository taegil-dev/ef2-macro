_LEFT_WINDOW_X = 0.335
_RIGHT_WINDOW_X = 0.658
_WIDTH = _RIGHT_WINDOW_X - _LEFT_WINDOW_X

region = {
    "GOLD_POS": (0.603, 0.55, 0.645, 0.58),
    "DIAMOND_POS": (0.47, 0.55, 0.53, 0.58),
    "MEDAL_POS": (0.53, 0.55, 0.58, 0.58),
    "WAVE_POS": (0.46, 0.01, 0.526, 0.027),
    "WAVE_POS2": (0.45, 0.285, 0.55, 0.35),
    "TIMER_POS": (0.40, 0.55, 0.46, 0.578),
    "REBIRTH_POS": (0.357, 0.129, 0.641, 0.321),
    "CONTINUE_POS": (0.569, 0.429, 0.631, 0.491)
}

pos = {
    "프리셋 변경 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.49),
    "첫번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.66),
    "두번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.14, 0.66),
    "세번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.18, 0.66),
    "네번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.22, 0.66),
    "다섯번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.26, 0.66),
    "여섯번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.30, 0.66),
    "일곱번째 펫 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.7),
    "병사 레벨업 감소 펫 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.66),

    "첫번째 유물 버튼": ("click", _LEFT_WINDOW_X + 0.06, 0.4),
    "두번째 유물 버튼": ("click", _LEFT_WINDOW_X + 0.11, 0.4),
    "세번째 유물 버튼": ("click", _LEFT_WINDOW_X + 0.16, 0.4),
    "네번째 유물 버튼": ("click", _LEFT_WINDOW_X + 0.21, 0.4),
    "다섯번째 유물 버튼": ("click", _LEFT_WINDOW_X + 0.26, 0.4),

    "첫번째 영웅 버튼": ("click", _LEFT_WINDOW_X + 0.06, 0.18),
    "두번째 영웅 버튼": ("click", _LEFT_WINDOW_X + 0.11, 0.18),
    "세번째 영웅 버튼": ("click", _LEFT_WINDOW_X + 0.16, 0.18),
    "네번째 영웅 버튼": ("click", _LEFT_WINDOW_X + 0.21, 0.18),
    "다섯번째 영웅 버튼": ("click", _LEFT_WINDOW_X + 0.26, 0.18),
    "프리셋 변경 저장 버튼": ("click", _LEFT_WINDOW_X + 0.12, 0.85),
    "프리셋 변경 취소 버튼": ("click", _LEFT_WINDOW_X + 0.2, 0.85),
    
    "2배 환생 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),
    "이어하기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.05, 0.45),

    "길드 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.05, 0.15),
    "건물 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.01, 0.97),
    "놀이터 버튼": ("click", _LEFT_WINDOW_X + 0.15, 0.49),
    "양궁 시작 버튼": ("click", _LEFT_WINDOW_X + 0.16, 0.65),
    "양궁 닫기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.01, 0.13),
    "길드 닫기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.01, 0.2),

    "퀘스트 탭": ("click", _LEFT_WINDOW_X + 0.03, 0.97),
    "스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.85, _LEFT_WINDOW_X + 0.03, 0.7, 0.1, 3),
    "정스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.68, _LEFT_WINDOW_X + 0.03, 0.75, 0.1, 1),
    "29 퀘스트 오픈 및 강화 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.82),
    "30 퀘스트 오픈 및 강화 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.89),
    "29 퀘스트 레벨업 맥스 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.82),
    "30 퀘스트 레벨업 맥스 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.88),

    "성 탭": ("click", _LEFT_WINDOW_X + 0.14, 0.97),
    "성 자동 강화 버튼": ("click", _LEFT_WINDOW_X + 0.03, 0.62),
    "성채 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.09, 0.6),
    "비서 버튼": ("click", _LEFT_WINDOW_X + 0.28, 0.65),
    "비서 확인 버튼": ("click", 0.49, 0.35),
    "비서 완료 버튼": ("click", _LEFT_WINDOW_X + 0.15, 0.82),

    "영웅 탭": ("click", _LEFT_WINDOW_X + 0.09, 0.97),
    "영웅 프리셋 활성화 버튼": ("click", 0.52, 0.6),
    "첫번째 영웅 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.04, 0.65),
    "두번째 영웅 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.10, 0.65),
    "세번째 영웅 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.16, 0.65),
    "네번째 영웅 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.22, 0.65),
    "다섯번째 영웅 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.28, 0.65),
    "영웅 프리셋 확인 버튼": ("click", _LEFT_WINDOW_X + 0.12, 0.35),

    "영웅 자동 강화 버튼": ("click", _LEFT_WINDOW_X + 0.055, 0.6),
    "영웅 강화 탭": ("click", _LEFT_WINDOW_X + 0.15, 0.6),
    "영웅 전체 선택 버튼": ("click", _LEFT_WINDOW_X + 0.04, 0.44),
    "영웅 1000 강화 버튼": ("click", _LEFT_WINDOW_X + 0.07, 0.9),
    "영웅 100 강화 버튼": ("click", _LEFT_WINDOW_X + 0.13, 0.9),
    "영웅 10 강화 버튼": ("click", _LEFT_WINDOW_X + 0.20, 0.9),
    "영웅 1 강화 버튼": ("click", _LEFT_WINDOW_X + 0.26, 0.9),

    "마지막 영웅 클릭": ("click", _LEFT_WINDOW_X + 0.09, 0.91),
    "영웅 상세 버튼": ("click", _LEFT_WINDOW_X + 0.03, 0.3),
    "영웅 해제 버튼": ("click", _LEFT_WINDOW_X + 0.2, 0.97),
    "영웅 닫기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.01, 0.15),

    "병영 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.09, 0.6),
    "인간 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.18, 0.6),
    "엘프 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.15, 0.6),
    "언데드 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.6),
    "오크 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.6),
    "나가 배치 스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.8, _LEFT_WINDOW_X + 0.03, 0.65, 0.5, 3),
    "나가 배치 역스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.68, _LEFT_WINDOW_X + 0.03, 0.73, 0.5, 2),
    "영웅 나가 배치 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.02, 0.73),

    "영입 및 구매 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.6),
    "영입 새로고침 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.6),
    "영입 새로고침 실패 시 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),

    "중앙 성": ("click", 0.5, 0.26),
    "영웅 배치 확인 버튼": ("click", 0.47, 0.55),
    "왼쪽 영웅": ("click", 0.45, 0.25),
    "왼쪽 대각 위 영웅": ("click", 0.46, 0.2),
    "왼쪽 위 영웅": ("click", 0.49, 0.18),
    "왼쪽 대각 아래 영웅": ("click", 0.46, 0.3),
    "왼쪽 아래 영웅": ("click", 0.49, 0.32),

    "오른쪽 영웅": ("click", 0.55, 0.25),
    "오른쪽 대각 위 영웅": ("click", 0.54, 0.2),
    "오른쪽 위 영웅": ("click", 0.51, 0.18),
    "오른쪽 대각 아래 영웅": ("click", 0.54, 0.3),
    "오른쪽 아래 영웅": ("click", 0.51, 0.32),

    "왼쪽 대각 아래 영웅 to 중앙": ("swipe", 0.46, 0.3, 0.5, 0.26, 0.5, 1),
    "왼쪽 아래 영웅 to 중앙": ("swipe", 0.49, 0.32, 0.5, 0.26, 0.5, 1),
    "오른쪽 대각 아래 영웅 to 중앙": ("swipe", 0.54, 0.3, 0.5, 0.26, 0.5, 1),
    "오른쪽 아래 영웅 to 중앙": ("swipe", 0.51, 0.32, 0.5, 0.26, 0.5, 1),

    "오른쪽 대각 위 영웅 to 왼쪽": ("swipe", 0.54, 0.2, 0.47, 0.29, 0.5, 1),
    "오른쪽 위 영웅 to 왼쪽 대각 아래": ("swipe", 0.51, 0.18, 0.5, 0.35, 0.5, 1),
    "오른쪽 대각 위 영웅 to 오른쪽 아래": ("swipe", 0.54, 0.2, 0.52, 0.35, 0.5, 1),

    "왼쪽 대각 위 영웅 뒤집기": ("swipe", 0.46, 0.2, 0.46, 0.35, 0.5, 1),
    "오른쪽 대각 위 영웅 뒤집기": ("swipe", 0.54, 0.2, 0.54, 0.35, 0.5, 1),
    "오른쪽 위 영웅 뒤집기": ("swipe", 0.51, 0.18, 0.51, 0.38, 0.5, 1),
}