__all__ = ["macros"]

_LEFT_WINDOW_X = 0.335
_RIGHT_WINDOW_X = 0.658
_WIDTH = _RIGHT_WINDOW_X - _LEFT_WINDOW_X

_pos = {
    "프리셋 변경 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.1, 0.49),
    "퀘스트 오픈 프리셋 변경 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.15, 0.4),
    "퀘스트 오픈 펫 변경 버튼": ("click", _LEFT_WINDOW_X + 0.14, 0.66),
    "등반 펫 변경 버튼": ("click", _LEFT_WINDOW_X + 0.1, 0.66),
    "등반 프리셋 변경 버튼": ("click", _LEFT_WINDOW_X + 0.09, 0.4),
    "프리셋 변경 저장 버튼": ("click", _LEFT_WINDOW_X + 0.12, 0.85),
    

    "2배 환생 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),
    "이어하기 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.09, 0.47),

    "퀘스트 탭": ("click", _LEFT_WINDOW_X + 0.03, 0.97),
    "퀘스트 스와이프": ("swipe", _LEFT_WINDOW_X + 0.03, 0.88, _LEFT_WINDOW_X + 0.03, 0.68, 0.1, 3),
    "30 퀘스트 오픈 및 강화 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.89),

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

    "영입 및 구매 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.04, 0.6),
    "영입 새로고침 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.6),
    "영입 새로고침 실패 시 버튼": ("click", _LEFT_WINDOW_X + _WIDTH - 0.12, 0.47),
    
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
    "퀘스트 레벨 확장 시퀀스": [
        _pos["퀘스트 탭"],
        _pos["퀘스트 스와이프"],
        _pos["퀘스트 스와이프"],
        _pos["퀘스트 스와이프"],

    ],
    "30 퀘스트 오픈 시퀀스": [
        _pos["퀘스트 탭"],
        _pos["퀘스트 스와이프"],
        _pos["퀘스트 스와이프"],
        _pos["퀘스트 스와이프"],

        _pos["프리셋 변경 버튼"],
        _pos["퀘스트 오픈 프리셋 변경 버튼"],
        _pos["퀘스트 오픈 펫 변경 버튼"],
        _pos["프리셋 변경 저장 버튼"],

        _pos["30 퀘스트 오픈 및 강화 버튼"],

        _pos["프리셋 변경 버튼"],
        _pos["등반 프리셋 변경 버튼"],
        _pos["등반 펫 변경 버튼"],
        _pos["프리셋 변경 저장 버튼"],
        _pos["퀘스트 탭"],
    ],
    "8000 영웅 프리셋 변경 시퀀스": [
        _pos["영웅 탭"],
        _pos["세번째 영웅 프리셋 버튼"],
        _pos["영웅 프리셋 확인 버튼"],

        _pos["영웅 자동 강화 버튼"],
        _pos["영웅 자동 강화 버튼"],
        _pos["영웅 탭"],
    ],
    "테스트 시퀀스": [
    ],
}

macros = {
    "환생": [
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 7000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
    ],
    "영휴": [
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 7000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
        {"condition": "wave", "goal": 5000, "sequence": _sequence["퀘스트 레벨 확장 시퀀스"]},
    ],
    "테스트": [

    ] 
}