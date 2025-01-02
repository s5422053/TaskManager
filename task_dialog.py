from PyQt5.QtWidgets import QMessageBox,QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton
from PyQt5.QtCore import QDate

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("タスクを編集" if task_data else "タスクを追加")
        self.setFixedSize(300, 300)

        # レイアウト
        layout = QVBoxLayout()

        # 入力フィールド
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("タスクのタイトルを入力")
        layout.addWidget(QLabel("タイトル:"))
        layout.addWidget(self.title_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("詳細を入力")
        layout.addWidget(QLabel("詳細:"))
        layout.addWidget(self.description_input)

        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate())
        self.due_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("締切日:"))
        layout.addWidget(self.due_date_input)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["低", "中", "高"])
        layout.addWidget(QLabel("優先度:"))
        layout.addWidget(self.priority_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["未着手", "進行中", "完了"])
        layout.addWidget(QLabel("状態:"))
        layout.addWidget(self.status_input)

        # 初期値を設定（編集モードの場合）
        if task_data:
            self.title_input.setText(task_data.get("title", "未設定"))
            self.description_input.setText(task_data.get("description", "なし"))
            due_date = task_data.get("due_date", QDate.currentDate().toString("yyyy-MM-dd"))
            self.due_date_input.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
            priority = task_data.get("priority", 1)  # デフォルトは「低」
            self.priority_input.setCurrentIndex(priority - 1)
            self.status_input.setCurrentText(task_data.get("status", "未着手"))

        # ボタン
        self.submit_button = QPushButton("保存" if task_data else "追加")
        self.submit_button.clicked.connect(self.validate_inputs)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def validate_inputs(self):
        # 入力検証
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "入力エラー", "タイトルを入力してください。")
            return

        if self.due_date_input.date() < QDate.currentDate():
            QMessageBox.warning(self, "入力エラー", "締切日は今日以降の日付を選択してください。")
            return

        self.accept()

    def get_task_data(self):
        # 入力データを取得
        return {
            "title": self.title_input.text(),
            "description": self.description_input.text(),
            "due_date": self.due_date_input.date().toString("yyyy-MM-dd"),
            "priority": self.priority_input.currentIndex() + 1,
            "status": self.status_input.currentText(),
        }
