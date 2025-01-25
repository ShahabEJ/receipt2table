import os
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QWidget,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

# Local imports
import services
from exporter import export_table_to_excel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Receipt to Table")
        self.setGeometry(200, 200, 600, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #7a7a7a;
                color: #d3d3d3;
            }
        """)

        # Fonts
        font_large = QFont("Arial", 16, QFont.Bold)

        # Image Display
        self.image_label = QLabel("No Image Loaded", alignment=Qt.AlignCenter)
        self.image_label.setFixedSize(400, 200)

        # QTableWidget to display parsed JSON
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget {
                color: #ffffff;
                gridline-color: #4CAF50;
                background-color: #1e1e1e;
            }
            QHeaderView::section {
                background-color: #6e9671;
                color: black;
            }
        """)

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Buttons
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)

        self.process_button = QPushButton("Process Receipt ")
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)

        # Export to Excel button
        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setEnabled(False)  # Enabled after table is populated

        # Layouts
        top_button_layout = QHBoxLayout()
        top_button_layout.addWidget(self.load_button)
        top_button_layout.addWidget(self.process_button)
        top_button_layout.setSpacing(20)

        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addWidget(self.export_button, alignment=Qt.AlignRight)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(top_button_layout)
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(bottom_button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.image_path = None

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            self.process_button.setEnabled(True)

    def process_image(self):
        if not self.image_path:
            return

        self.process_button.setText("Processing...")
        self.process_button.setEnabled(False)
        QApplication.processEvents()  # Force UI update

        # 1) Extract text from the image
        try:
            extracted_text = services.extract_text_from_image(self.image_path)
        except Exception as e:
            self.show_error(f"Error extracting text: {e}")
            self.restore_button()
            return

        # 2) Send text to GPT with function calling
        try:
            data = services.get_receipt_data_from_gpt(extracted_text)
            self.display_table(data)
        except ValueError as ve:
            # If GPT didn't return a function call or something
            self.show_error(str(ve))
        except Exception as e:
            self.show_error(f"Error during GPT analysis: {e}")
        finally:
            # Restore the button text and enable
            self.restore_button()

    def restore_button(self):
        """Restore the 'Process Receipt' button label and enable it."""
        self.process_button.setText("Process Receipt")
        self.process_button.setEnabled(True)

    def display_table(self, data: dict):

        items = data.get("items", [])
        total = data.get("total", 0)

        total_rows = len(items) + 1
        self.table_widget.clear()
        self.table_widget.setRowCount(total_rows)
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Item", "Price", "Quantity"])

        # Fill item rows
        for row_index, item in enumerate(items):
            description = item.get("description", "")
            price = item.get("price", 0)
            quantity = item.get("quantity", 0)

            self.table_widget.setItem(row_index, 0, QTableWidgetItem(str(description)))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(str(price)))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(str(quantity)))

        last_row_index = total_rows - 1
        self.table_widget.setItem(last_row_index, 0, QTableWidgetItem("TOTAL"))
        self.table_widget.setItem(last_row_index, 1, QTableWidgetItem(str(total)))
        self.table_widget.setItem(last_row_index, 2, QTableWidgetItem("—"))

        self.export_button.setEnabled(True)

    def export_to_excel(self):
        if self.table_widget.rowCount() == 0:
            self.show_error("No data in the table to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as Excel",
            "",
            "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        # If user didn't add ".xlsx", add it automatically
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            export_table_to_excel(self.table_widget, file_path)
            QMessageBox.information(self, "Success", f"Table exported successfully:\n{file_path}")
        except Exception as e:
            self.show_error(f"Could not save file:\n{e}")

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
