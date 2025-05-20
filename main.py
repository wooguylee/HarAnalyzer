# main.py

import sys
import os
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

class HARViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HAR 편집기")
        self.resize(1200, 700)

        self.har_folder = None
        self.current_entries = []
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # === 좌측: HAR 파일 리스트 ===
        self.har_list = QListWidget()
        self.har_list.itemClicked.connect(self.load_har_file)

        # === 중앙: Request 리스트 ===
        self.request_list = QListWidget()
        self.request_list.itemClicked.connect(self.display_request_detail)
        self.request_list.setSelectionMode(QListWidget.MultiSelection)

        # === 우측: 상세 보기 + 버튼 + 로그 ===
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)

        self.save_button = QPushButton("선택된 Request 저장")
        self.save_button.clicked.connect(self.save_selected_requests)

        btn_open_folder = QPushButton("HAR 폴더 열기")
        btn_open_folder.clicked.connect(self.open_folder)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        right_layout = QVBoxLayout()
        right_layout.addWidget(btn_open_folder)
        right_layout.addWidget(self.save_button)
        right_layout.addWidget(QLabel("Request 상세 보기"))
        right_layout.addWidget(self.detail_view, 2)
        right_layout.addWidget(QLabel("로그"))
        right_layout.addWidget(self.log_output, 1)

        layout = QHBoxLayout()
        layout.addWidget(self.har_list, 2)
        layout.addWidget(self.request_list, 4)
        layout.addLayout(right_layout, 4)

        main_widget.setLayout(layout)

    def log(self, msg):
        self.log_output.append(msg)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "HAR 파일 폴더 선택")
        if folder:
            self.har_folder = folder
            self.har_list.clear()
            for file in os.listdir(folder):
                if file.endswith(".har"):
                    self.har_list.addItem(file)
            self.log(f"폴더 열기 완료: {folder}")

    def load_har_file(self, item: QListWidgetItem):
        self.request_list.clear()
        self.detail_view.clear()

        filename = item.text()
        filepath = os.path.join(self.har_folder, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_entries = data.get("log", {}).get("entries", [])
            for entry in self.current_entries:
                url = entry.get("request", {}).get("url", "UNKNOWN")
                list_item = QListWidgetItem(url)
                list_item.setCheckState(Qt.Unchecked)
                self.request_list.addItem(list_item)
            self.log(f"{filename} 로드 완료 - Request 수: {len(self.current_entries)}")
        except Exception as e:
            QMessageBox.critical(self, "에러", f"HAR 파일을 여는 중 오류 발생:\n{e}")

    def display_request_detail(self, item: QListWidgetItem):
        index = self.request_list.row(item)
        if 0 <= index < len(self.current_entries):
            req = self.current_entries[index].get("request", {})
            detail_lines = [
                f"Method: {req.get('method', '')}",
                f"URL: {req.get('url', '')}",
                f"HTTP Version: {req.get('httpVersion', '')}",
                "\n--- Headers ---"
            ]
            for header in req.get("headers", []):
                detail_lines.append(f"{header.get('name')}: {header.get('value')}")
            if req.get("postData"):
                detail_lines.append("\n--- Post Data ---")
                detail_lines.append(req.get("postData", {}).get("text", ""))
            self.detail_view.setPlainText("\n".join(detail_lines))

    def save_selected_requests(self):
        selected_indexes = [
            i for i in range(self.request_list.count())
            if self.request_list.item(i).checkState() == Qt.Checked
        ]
        if not selected_indexes:
            QMessageBox.warning(self, "알림", "선택된 Request가 없습니다.")
            return

        selected_entries = [self.current_entries[i] for i in selected_indexes]
        new_har = {
            "log": {
                "version": "1.2",
                "creator": {"name": "HAR 편집기", "version": "1.0"},
                "entries": selected_entries
            }
        }

        save_path, _ = QFileDialog.getSaveFileName(self, "저장할 HAR 파일", "filtered.har", "HAR Files (*.har)")
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(new_har, f, ensure_ascii=False, indent=2)
            self.log(f"선택된 요청 저장 완료: {save_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = HARViewer()
    viewer.show()
    sys.exit(app.exec())
