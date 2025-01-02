import sqlite3
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QComboBox,QDialog,QMessageBox ,QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QInputDialog
from task_dialog import TaskDialog
from task_login import LoginDialog
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.user_id = user_id  # ログイン中のユーザーID
        self.setWindowTitle(f"Task Manager - ユーザーID: {user_id}")
        self.setGeometry(100, 100, 430, 600)

        # データベース接続
        self.conn = sqlite3.connect('task_manager.db')
        self.cursor = self.conn.cursor()

        # メインウィジェットとレイアウト
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # 検索バーとフィルタリング
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("タイトルを検索")
        self.search_bar.textChanged.connect(self.apply_filters)
        search_layout.addWidget(self.search_bar)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["すべて", "未着手", "進行中", "完了"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        search_layout.addWidget(self.status_filter)

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["すべて", "低", "中", "高"])
        self.priority_filter.currentIndexChanged.connect(self.apply_filters)
        search_layout.addWidget(self.priority_filter)

        layout.addLayout(search_layout)

        # タスク一覧テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 列数を6に設定（タイトル、締切日、ステータス、優先度、タスクID、詳細）
        self.table.setHorizontalHeaderLabels(["タイトル", "締切日", "ステータス", "優先度", "タスクID", "詳細"])
        self.table.setSortingEnabled(True)  # 並び替えを有効にする
        layout.addWidget(self.table)

        # タスクをダブルクリックで編集する
        self.table.cellDoubleClicked.connect(self.edit_task)

        # ボタン
        add_button = QPushButton("タスクを追加")
        edit_button = QPushButton("タスクを編集")
        delete_button = QPushButton("タスクを削除")
        layout.addWidget(add_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        # レイアウトの設定
        main_widget.setLayout(layout)

        # ボタンの動作
        add_button.clicked.connect(self.add_task)
        edit_button.clicked.connect(self.edit_task)
        delete_button.clicked.connect(self.delete_task)

        # アプリ起動時にタスクをロード
        self.load_tasks()

    def load_tasks(self):
        self.table.setRowCount(0)  # テーブルをクリア
        self.cursor.execute(
            "SELECT task_id, title, description, due_date, priority, status FROM tasks WHERE user_id = ?",
            (self.user_id,)
        )
        for row_data in self.cursor.fetchall():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # 表示する列
            title_item = QTableWidgetItem(row_data[1] if row_data[1] else "未設定")  # タイトルが空の場合にデフォルト値を設定
            self.table.setItem(row_position, 0, title_item)

            due_date_item = QTableWidgetItem(row_data[3] if row_data[3] else "未設定")  # 締切日が空の場合にデフォルト値を設定
            self.table.setItem(row_position, 1, due_date_item)

            status_item = QTableWidgetItem(row_data[5] if row_data[5] else "未着手")  # ステータスが空の場合にデフォルト値を設定
            self.table.setItem(row_position, 2, status_item)

            priority_text = ["低", "中", "高"][row_data[4] - 1] if row_data[4] else "低"
            priority_item = QTableWidgetItem(priority_text)
            priority_item.setData(Qt.UserRole, row_data[4] if row_data[4] else 1)  # 優先度が空の場合にデフォルト値を設定
            self.table.setItem(row_position, 3, priority_item)

            task_id_item = QTableWidgetItem(str(row_data[0]) if row_data[0] else "")
            self.table.setItem(row_position, 4, task_id_item)

            description_item = QTableWidgetItem(row_data[2] if row_data[2] else "なし")  # 詳細が空の場合にデフォルト値を設定
            self.table.setItem(row_position, 5, description_item)

        self.table.hideColumn(4)  # タスクID列を非表示
        self.table.hideColumn(5)  # 詳細列を非表示

        # 締切日（1列目）で昇順ソート
        self.table.sortItems(1, Qt.AscendingOrder)


    def add_task(self):
        # タスク追加ダイアログを表示
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()

            self.table.sortItems(4, Qt.AscendingOrder) #ソートを一時解除
        
            # データベースに新しいタスクを追加
            self.cursor.execute(
                "INSERT INTO tasks (title, description, due_date, priority, status, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                (task_data["title"], task_data["description"], task_data["due_date"],
                task_data["priority"], task_data["status"], self.user_id)
            )
            self.conn.commit()
            self.load_tasks()  # 再読み込み


    def edit_task(self, row=None, column=None):
        # 行が指定された場合（ダブルクリック時）、その行を使用
        if row is not None:
            current_row = row
        else:
            current_row = self.table.currentRow()  # 現在選択中の行を取得

        # 行が選択されていない場合はエラーメッセージを表示
        if current_row < 0:
            QMessageBox.warning(self, "エラー", "編集するタスクを選択してください。")
            return

        # タスクIDを非表示列から取得
        task_id_item = self.table.item(current_row, 4)  # タスクID列（非表示列）
        if not task_id_item or not task_id_item.text():
            QMessageBox.warning(self, "エラー", "タスクIDを取得できません。")
            return

        task_id = task_id_item.text()

        # データベースから選択されたタスクの詳細情報を取得
        try:
            self.cursor.execute(
                "SELECT title, description, due_date, priority, status FROM tasks WHERE task_id = ?",
                (task_id,)
            )
            task_data = self.cursor.fetchone()
            if not task_data:
                QMessageBox.warning(self, "エラー", "タスク情報を取得できません。")
                return

            # 編集用データを辞書形式で準備
            task_data_dict = {
                "title": task_data[0],
                "description": task_data[1],
                "due_date": task_data[2],
                "priority": task_data[3],
                "status": task_data[4],
            }

            # 編集ダイアログを表示
            dialog = TaskDialog(self, task_data_dict)
            if dialog.exec_() == QDialog.Accepted:
                new_data = dialog.get_task_data()
                
                # データベースを更新
                self.cursor.execute(
                    """
                    UPDATE tasks 
                    SET title = ?, description = ?, due_date = ?, priority = ?, status = ? 
                    WHERE task_id = ?
                    """,
                    (new_data["title"], new_data["description"], new_data["due_date"],
                    new_data["priority"], new_data["status"], task_id)
                )
                self.conn.commit()
                self.load_tasks()  # 再読み込み
                QMessageBox.information(self, "成功", "タスクが更新されました。")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"タスク編集中にエラーが発生しました: {e}")


    def delete_task(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "エラー", "削除するタスクを選択してください。")
            return

        task_id_item = self.table.item(current_row, 4)  # タスクID列（非表示列）
        if not task_id_item or not task_id_item.text():
            QMessageBox.warning(self, "エラー", "タスクIDを取得できません。")
            return

        task_id = task_id_item.text()

        reply = QMessageBox.question(self, "確認", "選択したタスクを削除しますか？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.table.sortItems(4, Qt.AscendingOrder) #ソートを一時解除
                self.cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
                self.conn.commit()
                self.load_tasks()  # 再読み込み
                QMessageBox.information(self, "成功", "タスクが削除されました。")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"タスク削除中にエラーが発生しました: {e}")


    def closeEvent(self, event):
        self.conn.close()
        event.accept()

    def apply_filters(self):
        search_text = self.search_bar.text().lower()
        status_text = self.status_filter.currentText()
        priority_text = self.priority_filter.currentText()

        for row in range(self.table.rowCount()):
            title = self.table.item(row, 0).text().lower()
            status = self.table.item(row, 2).text()
            priority = self.table.item(row, 3).text()

            # フィルタ条件に一致するか確認
            matches_search = search_text in title
            matches_status = status_text == "すべて" or status_text == status
            matches_priority = priority_text == "すべて" or priority_text == priority

            # 条件を満たさない場合は非表示にする
            self.table.setRowHidden(row, not (matches_search and matches_status and matches_priority))


if __name__ == "__main__":
    app = QApplication([])
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        window = MainWindow(login_dialog.user_id)
        window.show()
        app.exec_()
