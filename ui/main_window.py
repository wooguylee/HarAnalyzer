# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget
from json_diff import get_json_diff

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Diff Viewer")
        self.resize(800, 600)

        self.file1 = None
        self.file2 = None

        layout = QVBoxLayout()

        self.btn_load_file1 = QPushButton("Load JSON 1")
        self.btn_load_file2 = QPushButton("Load JSON 2")
        self.btn_compare = QPushButton("Compare")

        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)

        self.btn_load_file1.clicked.connect(lambda: self.load_file(1))
        self.btn_load_file2.clicked.connect(lambda: self.load_file(2))
        self.btn_compare.clicked.connect(self.compare)

        layout.addWidget(self.btn_load_file1)
        layout.addWidget(self.btn_load_file2)
        layout.addWidget(self.btn_compare)
        layout.addWidget(self.text_result)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_path:
            if index == 1:
                self.file1 = file_path
                self.btn_load_file1.setText(f"Loaded: {file_path.split('/')[-1]}")
            else:
                self.file2 = file_path
                self.btn_load_file2.setText(f"Loaded: {file_path.split('/')[-1]}")

    def compare(self):
        if self.file1 and self.file2:
            result = get_json_diff(self.file1, self.file2)
            self.text_result.setPlainText(result)
        else:
            self.text_result.setPlainText("Both JSON files must be loaded.")
