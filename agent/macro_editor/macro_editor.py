import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QAbstractItemView, QComboBox, QFileDialog, QHBoxLayout,
    QInputDialog, QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QSplitter, QTabWidget, QVBoxLayout, QWidget,
)
import ef2.pos as p

BASE_DIR = Path(__file__).resolve().parent


def read_json(name):
    path = BASE_DIR / name
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def write_json(name, data):
    path = BASE_DIR / name
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('매크로 에디터')
        self.resize(1600, 900)
        self.color = Qt.black

        # 파일 로드
        self.positions = read_json('positions.json')
        self.delays = read_json('delays.json')
        self.sequences = read_json('sequences.json')
        self.macros = read_json('macros.json')
        self.changed = False

        root = QWidget()
        layout = QVBoxLayout(root)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setCentralWidget(root)

        self.sequence_tab = QWidget()
        self.macro_tab = QWidget()
        self.tabs.addTab(self.sequence_tab, '시퀀스 편집')
        self.tabs.addTab(self.macro_tab, '매크로 편집')
        self.build_sequences()
        self.build_macros()

        bottom = QHBoxLayout()
        self.status = QLabel('기존 JSON 데이터를 불러왔습니다.')
        bottom.addWidget(self.status, 1)
        save_btn = QPushButton('JSON 저장 (Ctrl+S)')
        save_btn.clicked.connect(self.save)
        bottom.addWidget(save_btn)
        layout.addLayout(bottom)
        from PySide6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence.Save, self, activated=self.save)
        self.refresh_sequences()
        self.refresh_macros()

    def button(self, text, callback, parent_layout):
        b = QPushButton(text)
        b.clicked.connect(callback)
        parent_layout.addWidget(b)
        return b

    def build_sequences(self):
        layout = QHBoxLayout(self.sequence_tab)
        left = QVBoxLayout()
        left.addWidget(QLabel('시퀀스 목록'))
        self.seq_names = QListWidget()
        self.seq_names.currentTextChanged.connect(self.show_sequence)
        left.addWidget(self.seq_names)
        row = QHBoxLayout()
        self.button('추가', self.add_sequence, row)
        self.button('이름 변경', self.rename_sequence, row)
        self.button('삭제', self.delete_sequence, row)
        left.addLayout(row)
        layout.addLayout(left, 2)

        center = QVBoxLayout()
        center.addWidget(QLabel('선택한 시퀀스의 실행 순서'))
        self.seq_steps = QListWidget()
        self.seq_steps.setSelectionMode(QAbstractItemView.SingleSelection)
        center.addWidget(self.seq_steps)
        row = QHBoxLayout()
        self.button('↑ 위로', lambda: self.move_step(-1), row)
        self.button('↓ 아래로', lambda: self.move_step(1), row)
        self.button('제거', self.remove_step, row)
        center.addLayout(row)
        layout.addLayout(center, 3)

        right = QVBoxLayout()
        right.addWidget(QLabel('미리 정의된 동작'))
        self.action_kind = QComboBox()
        self.action_kind.addItems(['POS', 'DELAY'])
        self.action_kind.currentIndexChanged.connect(self.refresh_actions)
        right.addWidget(self.action_kind)
        self.action_filter = QComboBox()
        self.action_filter.setEditable(True)
        self.action_filter.setInsertPolicy(QComboBox.NoInsert)
        self.action_filter.lineEdit().setPlaceholderText('목록에서 선택하거나 검색')
        right.addWidget(self.action_filter)
        self.action_list = QListWidget()
        self.action_list.itemDoubleClicked.connect(lambda _: self.add_step())
        right.addWidget(self.action_list)
        self.button('선택한 동작 추가 →', self.add_step, right)
        layout.addLayout(right, 2)
        self.action_filter.lineEdit().textEdited.connect(self.filter_actions)
        self.refresh_actions()

    def build_macros(self):
        layout = QHBoxLayout(self.macro_tab)
        left = QVBoxLayout()
        left.addWidget(QLabel('매크로 목록'))
        self.macro_names = QListWidget()
        self.macro_names.currentTextChanged.connect(self.show_macro)
        left.addWidget(self.macro_names)
        row = QHBoxLayout()
        self.button('추가', self.add_macro, row)
        self.button('이름 변경', self.rename_macro, row)
        self.button('삭제', self.delete_macro, row)
        left.addLayout(row)
        layout.addLayout(left, 2)

        center = QVBoxLayout()
        center.addWidget(QLabel('매크로에서 실행할 시퀀스 순서'))
        self.macro_steps = QListWidget()
        center.addWidget(self.macro_steps)
        row = QHBoxLayout()
        self.button('↑ 위로', lambda: self.move_block(-1), row)
        self.button('↓ 아래로', lambda: self.move_block(1), row)
        self.button('제거', self.remove_block, row)
        center.addLayout(row)
        layout.addLayout(center, 3)

        right = QVBoxLayout()
        right.addWidget(QLabel('사용할 시퀀스'))
        self.available_sequences = QListWidget()
        self.available_sequences.itemDoubleClicked.connect(lambda _: self.add_block())
        right.addWidget(self.available_sequences)
        self.button('선택한 시퀀스 추가 →', self.add_block, right)
        layout.addLayout(right, 2)

    def mark(self):
        self.changed = True
        self.status.setText('저장되지 않은 변경사항이 있습니다.')
        self.setWindowTitle('Macro Sequence Editor *')

    def refresh_sequences(self, select=None):
        current = select or self.seq_names.currentItem() and self.seq_names.currentItem().text()
        self.seq_names.blockSignals(True)
        self.seq_names.clear()
        self.seq_names.addItems(list(self.sequences))
        self.seq_names.blockSignals(False)
        if current in self.sequences:
            self.seq_names.setCurrentRow(list(self.sequences).index(current))
        elif self.sequences:
            self.seq_names.setCurrentRow(0)
        else:
            self.seq_steps.clear()
        self.refresh_available_sequences()

    def refresh_available_sequences(self):
        self.available_sequences.clear()
        self.available_sequences.addItems(list(self.sequences))

    def current_sequence(self):
        item = self.seq_names.currentItem()
        return item.text() if item else None

    def show_sequence(self, name):
        self.seq_steps.clear()
        for step in self.sequences.get(name, []):
            if step['type'] == 'custom_delay':
                label = f"딜레이 {step['seconds']}초"
            else:
                label = f"{step['type'].upper()}  |  {step['name']}"
            self.seq_steps.addItem(label)

    def refresh_actions(self):
        self.action_filter.blockSignals(True)
        self.action_filter.clear()
        self.action_filter.blockSignals(False)
        self.action_list.clear()
        values = self.positions if self.action_kind.currentText() == 'POS' else self.delays
        self.action_list.addItems(list(values))

    def filter_actions(self, query):
        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            item.setHidden(query.casefold() not in item.text().casefold())

    def add_sequence(self):
        name, ok = QInputDialog.getText(self, '새 시퀀스', '시퀀스 이름:')
        name = name.strip()
        if not ok or not name:
            return
        if name in self.sequences:
            QMessageBox.warning(self, '중복', '이미 존재하는 시퀀스입니다.')
            return
        self.sequences[name] = []
        self.mark()
        self.refresh_sequences(name)

    def rename_sequence(self):
        old = self.current_sequence()
        if not old: return
        name, ok = QInputDialog.getText(self, '이름 변경', '새 이름:', text=old)
        name = name.strip()
        if not ok or not name or name == old: return
        if name in self.sequences:
            QMessageBox.warning(self, '중복', '이미 존재하는 시퀀스입니다.')
            return
        self.sequences = {(name if k == old else k):v for k,v in self.sequences.items()}
        for blocks in self.macros.values():
            for block in blocks:
                if block['sequence'] == old: block['sequence'] = name
        self.mark()
        self.refresh_sequences(name)
        self.refresh_macros()

    def delete_sequence(self):
        name = self.current_sequence()
        if not name: return
        used = [k for k, blocks in self.macros.items() if any(b['sequence'] == name for b in blocks)]
        if used:
            QMessageBox.warning(self, '삭제 불가', '다음 매크로에서 사용 중입니다: ' + ', '.join(used))
            return
        if QMessageBox.question(self, '삭제', f'"{name}" 시퀀스를 삭제할까요?') != QMessageBox.Yes: return
        del self.sequences[name]
        self.mark()
        self.refresh_sequences()

    def add_step(self):
        name = self.current_sequence()
        item = self.action_list.currentItem()
        if not name or not item: return
        kind = 'pos' if self.action_kind.currentText() == 'POS' else 'delay'
        index = self.seq_steps.currentRow()
        at = index + 1 if index >= 0 else len(self.sequences[name])
        self.sequences[name].insert(at, {'type':kind, 'name':item.text()})
        self.mark()
        self.show_sequence(name)
        self.seq_steps.setCurrentRow(at)

    def move_step(self, delta):
        name = self.current_sequence()
        if not name: return
        a = self.seq_steps.currentRow()
        b = a + delta
        if a < 0 or b < 0 or b >= len(self.sequences[name]): return
        steps = self.sequences[name]
        steps[a],steps[b] = steps[b],steps[a]
        self.mark()
        self.show_sequence(name)
        self.seq_steps.setCurrentRow(b)

    def remove_step(self):
        name = self.current_sequence()
        i = self.seq_steps.currentRow()
        if not name or i < 0: return
        del self.sequences[name][i]
        self.mark()
        self.show_sequence(name)
        self.seq_steps.setCurrentRow(min(i, self.seq_steps.count()-1))

    def current_macro(self):
        item = self.macro_names.currentItem()
        return item.text() if item else None

    def refresh_macros(self, select=None):
        current = select or self.current_macro()
        self.macro_names.blockSignals(True)
        self.macro_names.clear()
        self.macro_names.addItems(list(self.macros))
        self.macro_names.blockSignals(False)
        if current in self.macros:
            self.macro_names.setCurrentRow(list(self.macros).index(current))
        elif self.macros:
            self.macro_names.setCurrentRow(0)
        else:
            self.macro_steps.clear()

    def show_macro(self, name):
        self.macro_steps.clear()
        for block in self.macros.get(name, []):
            self.macro_steps.addItem(f"{block['name']}  →  {block['sequence']}")

    def add_macro(self):
        name, ok = QInputDialog.getText(self, '새 매크로', '매크로 이름:')
        name = name.strip()
        if not ok or not name: return
        if name in self.macros:
            QMessageBox.warning(self, '중복', '이미 존재하는 매크로입니다.')
            return
        self.macros[name] = []
        self.mark()
        self.refresh_macros(name)

    def rename_macro(self):
        old = self.current_macro()
        if not old: return
        name, ok = QInputDialog.getText(self, '이름 변경', '새 이름:', text=old)
        name = name.strip()
        if not ok or not name or name == old: return
        if name in self.macros:
            QMessageBox.warning(self, '중복', '이미 존재하는 매크로입니다.')
            return
        self.macros = {(name if k == old else k):v for k,v in self.macros.items()}
        self.mark()
        self.refresh_macros(name)

    def delete_macro(self):
        name = self.current_macro()
        if not name: return
        if QMessageBox.question(self, '삭제', f'"{name}" 매크로를 삭제할까요?') != QMessageBox.Yes: return
        del self.macros[name]
        self.mark()
        self.refresh_macros()

    def add_block(self):
        name = self.current_macro()
        item = self.available_sequences.currentItem()
        if not name or not item: return
        sequence = item.text()
        index = self.macro_steps.currentRow()
        at = index + 1 if index >= 0 else len(self.macros[name])
        self.macros[name].insert(at, {'name':sequence,'sequence':sequence})
        self.mark()
        self.show_macro(name)
        self.macro_steps.setCurrentRow(at)

    def move_block(self, delta):
        name = self.current_macro()
        if not name: return
        a = self.macro_steps.currentRow()
        b = a + delta
        if a < 0 or b < 0 or b >= len(self.macros[name]): return
        blocks = self.macros[name]
        blocks[a],blocks[b] = blocks[b],blocks[a]
        self.mark()
        self.show_macro(name)
        self.macro_steps.setCurrentRow(b)

    def remove_block(self):
        name = self.current_macro()
        i = self.macro_steps.currentRow()
        if not name or i < 0: return
        del self.macros[name][i]
        self.mark()
        self.show_macro(name)
        self.macro_steps.setCurrentRow(min(i,self.macro_steps.count()-1))

    def save(self):
        try:
            write_json('sequences.json', self.sequences)
            write_json('macros.json', self.macros)
        except Exception as e:
            QMessageBox.critical(self, '저장 실패', str(e))
            return
        self.changed = False
        self.setWindowTitle('Macro Sequence Editor')
        self.status.setText('sequences.json, macros.json 저장 완료')

    def closeEvent(self, event):
        if self.changed:
            answer = QMessageBox.question(self, '저장되지 않은 변경사항', '변경사항을 저장할까요?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if answer == QMessageBox.Cancel:
                event.ignore(); return
            if answer == QMessageBox.Save:
                self.save()
                if self.changed:
                    event.ignore(); return
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QWidget {
            background-color: #18181b;
            color: #e4e4e7;
            font-size: 13px;
        }

        QMainWindow, QDialog {
            background-color: #18181b;
        }

        QTreeWidget, QListWidget, QTableWidget {
            background-color: #27272a;
            color: #e4e4e7;
            border: 1px solid #3f3f46;
            border-radius: 6px;
            outline: none;
        }

        QTreeWidget::item, QListWidget::item {
            padding: 6px;
        }

        QTreeWidget::item:selected,
        QListWidget::item:selected,
        QTableWidget::item:selected {
            background-color: #3b4260;
            color: #ffffff;
        }

        QPushButton {
            background-color: #3f3f46;
            color: #f4f4f5;
            border: 1px solid #52525b;
            border-radius: 6px;
            padding: 7px 12px;
        }

        QPushButton:hover {
            background-color: #52525b;
        }

        QPushButton:pressed {
            background-color: #6366f1;
        }

        QPushButton:disabled {
            background-color: #27272a;
            color: #71717a;
        }

        QLineEdit, QSpinBox, QDoubleSpinBox,
        QComboBox, QTextEdit {
            background-color: #27272a;
            color: #f4f4f5;
            border: 1px solid #52525b;
            border-radius: 5px;
            padding: 5px;
            selection-background-color: #4f46e5;
        }

        QLineEdit:focus, QSpinBox:focus,
        QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #818cf8;
        }

        QComboBox QAbstractItemView {
            background-color: #27272a;
            color: #f4f4f5;
            selection-background-color: #3b4260;
        }

        QTabWidget::pane {
            border: 1px solid #3f3f46;
            background-color: #18181b;
        }

        QTabBar::tab {
            background-color: #27272a;
            color: #a1a1aa;
            padding: 9px 18px;
            border: 1px solid #3f3f46;
        }

        QTabBar::tab:selected {
            background-color: #3f3f46;
            color: #ffffff;
        }

        QHeaderView::section {
            background-color: #27272a;
            color: #e4e4e7;
            padding: 6px;
            border: 1px solid #3f3f46;
        }

        QMenuBar, QMenu {
            background-color: #27272a;
            color: #e4e4e7;
        }

        QMenu::item:selected {
            background-color: #3f3f46;
        }

        QScrollBar:vertical {
            background-color: #18181b;
            width: 10px;
        }

        QScrollBar::handle:vertical {
            background-color: #52525b;
            border-radius: 5px;
            min-height: 20px;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0px;
            width: 0px;
        }

        QSplitter::handle {
            background-color: #3f3f46;
        }
    """)

    window = Editor()
    window.show()
    sys.exit(app.exec())
