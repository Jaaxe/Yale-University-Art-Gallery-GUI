import sys
import pickle
import socket
import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QErrorMessage
)
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

import dialog

def query_server(host, port, query_data):
    try:
        data = pickle.dumps(query_data)
    except pickle.PicklingError as e:
        raise Exception(f"Data serialization error: {e}")
    
    try:
        with socket.create_connection((host, port)) as sock:
            sock.sendall(data)
            with sock.makefile('rb') as f:
                response = pickle.load(f)
                return response
    except Exception as e:
        raise Exception(f"Communication error: {e}")

class MainWindow(QMainWindow):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YUAG Application")
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(100, 100, screen.width() // 2, screen.height() // 2)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Horizontal layout for the four QLineEdits
        input_layout = QHBoxLayout()

        # Label
        self.labelEdit = QLineEdit()
        self.labelEdit.setPlaceholderText("Label")

        # Classifier
        self.classifierEdit = QLineEdit()
        self.classifierEdit.setPlaceholderText("Classifier")

        # Agent
        self.agentEdit = QLineEdit()
        self.agentEdit.setPlaceholderText("Agent")

        # Date
        self.dateEdit = QLineEdit()
        self.dateEdit.setPlaceholderText("Date")

        input_layout.addWidget(self.labelEdit)
        input_layout.addWidget(self.classifierEdit)
        input_layout.addWidget(self.agentEdit)
        input_layout.addWidget(self.dateEdit)
        main_layout.addLayout(input_layout)

        # Submit button
        self.submitButton = QPushButton("Submit Query")
        main_layout.addWidget(self.submitButton)
        self.submitButton.clicked.connect(self.submitQuery)

        # Connect Enter key for all text fields
        self.labelEdit.returnPressed.connect(self.submitQuery)
        self.classifierEdit.returnPressed.connect(self.submitQuery)
        self.agentEdit.returnPressed.connect(self.submitQuery)
        self.dateEdit.returnPressed.connect(self.submitQuery)

        # Results list widget
        self.listWidget = QListWidget()
        self.listWidget.setFont(dialog.FW_FONT)
        main_layout.addWidget(self.listWidget)
        self.listWidget.itemDoubleClicked.connect(self.showDetails)

        shortcut = QShortcut(QKeySequence.Open, self.listWidget)
        shortcut.activated.connect(self.openSelectedItem)

    def openSelectedItem(self):
        item = self.listWidget.currentItem()
        if item:
            self.showDetails(item)

    def submitQuery(self):
        # Send the fields as { label, classifier, agent, date }
        query_data = {
            "label": self.labelEdit.text(),
            "classifier": self.classifierEdit.text(),
            "agent": self.agentEdit.text(),
            "date": self.dateEdit.text()
        }
        try:
            response = query_server(self.host, self.port, query_data)
        except Exception as e:
            err = QErrorMessage(self)
            err.showMessage(str(e))
            return

        results = response.get("list", [])
        self.listWidget.clear()

        for row in results[:1000]:
            # row = [id, label, date, agents, classifiers]
            object_id = row[0]
            label = (str(row[1]) or "")[:250]       
            date_ = (str(row[2]) or "")[:80]       
            agents = (str(row[3]) or "")[:180]      
            classifiers = (str(row[4]) or "")[:500]

            row_text = (
                f"{label:<250}"
                f"{date_:<80}"
                f"{agents:<180}"
                f"{classifiers:<500}"
            )

            item = QListWidgetItem(row_text)
            item.setData(Qt.UserRole, object_id)
            self.listWidget.addItem(item)

    def showDetails(self, item):
        object_id = item.data(Qt.UserRole)
        query_data = {"id": object_id}
        try:
            response = query_server(self.host, self.port, query_data)
        except Exception as e:
            err = QErrorMessage(self)
            err.showMessage(str(e))
            return
        details = response.get("details", {})

        d = dialog.FixedWidthMessageDialog(
            f"Details for object {object_id}",
            details
        )
        d.exec()

def parse_input():
    parser = argparse.ArgumentParser(description="Client for the YUAG application")
    parser.add_argument("host", help="the host on which the server is running")
    parser.add_argument("port", type=int, help="the port at which the server is listening")
    args = parser.parse_args()
    return args.host, args.port

def main():
    host, port = parse_input()
    app = QApplication(sys.argv)
    win = MainWindow(host, port)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
