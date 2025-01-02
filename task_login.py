import sqlite3
from PyQt5.QtWidgets import QHBoxLayout,QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from task_register import RegisterDialog

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ログイン")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # 入力フィールド
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("ユーザー名を入力")
        layout.addWidget(QLabel("ユーザー名:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("パスワードを入力")
        layout.addWidget(QLabel("パスワード:"))
        layout.addWidget(self.password_input)

        # ボタン
        button_layout = QHBoxLayout()
        login_button = QPushButton("ログイン")
        login_button.clicked.connect(self.validate_login)
        button_layout.addWidget(login_button)

        register_button = QPushButton("新規登録")
        register_button.clicked.connect(self.open_register_dialog)
        button_layout.addWidget(register_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 結果保持
        self.user_id = None

    def validate_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect('task_manager.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.user_id = result[0]
            self.accept()  # ログイン成功
        else:
            QMessageBox.warning(self, "エラー", "ユーザー名またはパスワードが間違っています。")

    def open_register_dialog(self):
        register_dialog = RegisterDialog(self)
        register_dialog.exec_()