from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import sqlite3

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新規ユーザー登録")
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

        # 登録ボタン
        register_button = QPushButton("登録")
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "入力エラー", "ユーザー名とパスワードを入力してください。")
            return

        try:
            conn = sqlite3.connect('task_manager.db')
            cursor = conn.cursor()

            # ユーザー名の重複チェック
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "登録エラー", "このユーザー名は既に使用されています。")
                return

            # ユーザーの登録
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "成功", "ユーザーが登録されました。")
            self.accept()  # 登録成功でダイアログを閉じる
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ユーザー登録中にエラーが発生しました: {e}")
