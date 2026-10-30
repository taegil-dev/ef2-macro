__all__ = ["macros", "GOLD_POS", "WAVE_POS"]

_LEFT_WINDOW_X = 0.335
_RIGHT_WINDOW_X = 0.658
_WIDTH = _RIGHT_WINDOW_X - _LEFT_WINDOW_X

GOLD_POS = 0.606, 0.55, 0.64, 0.58
WAVE_POS = 0.5, 0.01, 0.525, 0.027

_pos = {
    "프리셋 변경 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.49),
    "등반 펫 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.66),
    "퀘스트 오픈 펫 버튼": ("click", _LEFT_WINDOW_X + 0.14, 0.66),
    "퀘스트 확장 펫 버튼": ("click", _LEFT_WINDOW_X + 0.18, 0.66),
    "병사 레벨업 감소 펫 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.66),

    "등반 유물 프리셋 버튼": ("click", _LEFT_WINDOW_X + 0.09, 0.4),
    "퀘스트 오픈 유물 프리셋 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.15, 0.4),
    "병사 레벨업 감소 유물 프리셋 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.4),
    "프리셋 변경 저장 버튼": ("click", _LEFT_WINDOW_X + 0.12, 0.85),
    
    "2배 환생 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),
    "이어하기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.09, 0.47),

    "퀘스트 탭": ("click", _LEFT_WINDOW_X + 0.03, 0.97),
    "스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.9, _LEFT_WINDOW_X + 0.03, 0.68, 0.1, 2),
    "정스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.68, _LEFT_WINDOW_X + 0.03, 0.75, 0.1, 1),
    "29 퀘스트 오픈 및 강화 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.82),
    "30 퀘스트 오픈 및 강화 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.89),
    "29 퀘스트 레벨업 맥스 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.82),
    "30 퀘스트 레벨업 맥스 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.87),

    "성 탭": ("click", _LEFT_WINDOW_X + 0.14, 0.97),
    "성 자동 강화 버튼": ("click", _LEFT_WINDOW_X + 0.03, 0.62),

    "영웅 탭": ("click", _LEFT_WINDOW_X + 0.09, 0.97),
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

    "마지막 영웅 클릭": ("click", _LEFT_WINDOW_X + 0.09, 0.92),
    "영웅 상세 버튼": ("click", _LEFT_WINDOW_X + 0.03, 0.3),
    "영웅 해제 버튼": ("click", _LEFT_WINDOW_X + 0.2, 0.97),
    "영웅 닫기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.01, 0.15),

    "병영 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.09, 0.6),
    "인간 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.18, 0.6),
    "엘프 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.15, 0.6),
    "언데드 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.6),
    "오크 종족 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.6),
    "나가 배치 역스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.68, _LEFT_WINDOW_X + 0.03, 0.73, 0.5, 2),
    "영웅 나가 배치 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.02, 0.72),

    "영입 및 구매 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.6),
    "영입 새로고침 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.6),
    "영입 새로고침 실패 시 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),
}

_delay = {
    "짧은 딜레이": ("delay", 0.2),
    "긴 딜레이": ("delay", 1),
}

_sequence = {
    "영입 시퀀스": [
        _pos["영웅 탭"],
        _pos["영입 및 구매 버튼"],
        _pos["영입 새로고침 버튼"],
        _pos["영입 및 구매 버튼"],
        _pos["영입 새로고침 실패 시 버튼"],
        _pos["영웅 탭"],
    ],
    "등반 프리셋 시퀀스": [
        _pos["프리셋 변경 버튼"],
        _pos["등반 유물 프리셋 버튼"],
        _pos["등반 펫 버튼"],
        _pos["프리셋 변경 저장 버튼"],

        _delay["짧은 딜레이"],
    ],
    "퀘스트 확장 프리셋 시퀀스": [
        _pos["프리셋 변경 버튼"],
        _pos["퀘스트 확장 펫 버튼"],
        _pos["프리셋 변경 저장 버튼"],

        _delay["짧은 딜레이"],
    ],
    "퀘스트 오픈 프리셋 시퀀스": [
        _pos["프리셋 변경 버튼"],
        _pos["퀘스트 오픈 유물 프리셋 버튼"],
        _pos["퀘스트 오픈 펫 버튼"],
        _pos["프리셋 변경 저장 버튼"],

        _delay["짧은 딜레이"],
    ],
    "병사 레벨업 감소 프리셋 시퀀스": [
        _pos["프리셋 변경 버튼"],
        _pos["병사 레벨업 감소 유물 프리셋 버튼"],
        _pos["병사 레벨업 감소 펫 버튼"],
        _pos["프리셋 변경 저장 버튼"],

        _delay["짧은 딜레이"],
    ],
    "퀘스트 스와이프 시퀀스": [
        _pos["퀘스트 탭"],
        _pos["스와이프"],
        _pos["스와이프"],
        _pos["스와이프"],

        _delay["짧은 딜레이"],
    ],
    "29 퀘스트 오픈 및 레벨업 시퀀스": [
        _pos["퀘스트 탭"],
        _pos["29 퀘스트 오픈 및 강화 버튼"],
        _pos["29 퀘스트 오픈 및 강화 버튼"],
        _pos["29 퀘스트 오픈 및 강화 버튼"],
        _pos["29 퀘스트 레벨업 맥스 버튼"],
        _pos["퀘스트 탭"],
    ],
    "30 퀘스트 오픈 및 레벨업 시퀀스": [
        _pos["퀘스트 탭"],
        _pos["30 퀘스트 오픈 및 강화 버튼"],
        _pos["30 퀘스트 오픈 및 강화 버튼"],
        _pos["30 퀘스트 오픈 및 강화 버튼"],
        _pos["30 퀘스트 레벨업 맥스 버튼"],
        _pos["퀘스트 탭"],
    ],
    "8000 영웅 프리셋 변경 시퀀스": [
        _pos["영웅 탭"],
        _pos["세번째 영웅 프리셋 버튼"],
        _pos["영웅 프리셋 확인 버튼"],

        _pos["영웅 자동 강화 버튼"],
        _pos["영웅 자동 강화 버튼"],
    ],
    "9000 영웅 프리셋 변경 시퀀스": [
        _pos["영웅 탭"],
        _pos["네번째 영웅 프리셋 버튼"],
        _pos["영웅 프리셋 확인 버튼"],

        _pos["영웅 자동 강화 버튼"],
        _pos["영웅 자동 강화 버튼"],

        _pos["스와이프"],
        _pos["마지막 영웅 클릭"],
        _pos["영웅 상세 버튼"],
        _pos["영웅 해제 버튼"],

        _pos["마지막 영웅 클릭"],
        _pos["영웅 상세 버튼"],
        _pos["영웅 해제 버튼"],

        _pos["마지막 영웅 클릭"],
        _pos["영웅 상세 버튼"],
        _pos["영웅 해제 버튼"],

        _pos["마지막 영웅 클릭"],
        _pos["영웅 상세 버튼"],
        _pos["영웅 해제 버튼"],
    ],
    "영웅 나가 배치 시퀀스": [
        _pos["영웅 탭"],
        _pos["병영 버튼"],
        _pos["인간 종족 버튼"],
        _pos["엘프 종족 버튼"],
        _pos["언데드 종족 버튼"],

        _pos["스와이프"],
        _pos["나가 배치 역스와이프"],
        _pos["정스와이프"],

        _pos["영웅 나가 배치 버튼"],
        _pos["영웅 나가 배치 버튼"],
        _pos["영웅 나가 배치 버튼"],
        _pos["영웅 나가 배치 버튼"],
        _pos["영웅 탭"],

        _pos["영웅 자동 강화 버튼"],
        _pos["영웅 자동 강화 버튼"],
    ],
    "테스트 시퀀스": [

    ]
}

macros = {
    "자동 환생": [
    ],
    "영휴": [
    ],
    "영입": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["영입 시퀀스"]},
    ],
    "퀘스트 29 레벨업": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 확장 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 스와이프 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["29 퀘스트 오픈 및 레벨업 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["등반 프리셋 시퀀스"]},
    ],
    "퀘스트 30 오픈": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 오픈 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 스와이프 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["30 퀘스트 오픈 및 레벨업 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["등반 프리셋 시퀀스"]},
    ],
    "퀘스트 30 레벨업": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 확장 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["퀘스트 스와이프 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["30 퀘스트 오픈 및 레벨업 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["등반 프리셋 시퀀스"]},
    ],
    "웨이브 8000": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["8000 영웅 프리셋 변경 시퀀스"]},
    ],
    "웨이브 9000": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["병사 레벨업 감소 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["9000 영웅 프리셋 변경 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["등반 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["영웅 나가 배치 시퀀스"]},
    ],
    "테스트": [
        {"condition": "empty", "goal": 0, "sequence": _sequence["병사 레벨업 감소 프리셋 시퀀스"]},
        {"condition": "empty", "goal": 0, "sequence": _sequence["9000 영웅 프리셋 변경 시퀀스"]},
        # {"condition": "empty", "goal": 0, "sequence": _sequence["테스트 시퀀스"]},
        # {"condition": "empty", "goal": 0, "sequence": _sequence["9000 영웅 프리셋 변경 시퀀스"]},
    ] 
}