import xlsxwriter
from PySide6.QtWidgets import QTableWidget


def export_table_to_excel(table_widget: QTableWidget, file_path: str) -> None:

    # Create an Excel workbook and add a worksheet
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet("Receipt Data")

    # Write column headers
    col_count = table_widget.columnCount()
    for col in range(col_count):
        header_item = table_widget.horizontalHeaderItem(col)
        header_text = header_item.text() if header_item else f"Column {col}"
        worksheet.write(0, col, header_text)

    # Detect numeric columns by name, e.g. "Price" or "Quantity"
    numeric_cols = []
    for col in range(col_count):
        hdr = table_widget.horizontalHeaderItem(col).text().lower()
        if hdr in ("price", "quantity"):
            numeric_cols.append(col)

    # Write table rows
    row_count = table_widget.rowCount()
    for row in range(row_count):
        for col in range(col_count):
            item = table_widget.item(row, col)
            value = item.text() if item else ""

            xlsx_row = row + 1

            if col in numeric_cols:
                try:
                    numeric_val = float(value)
                    worksheet.write_number(xlsx_row, col, numeric_val)
                    continue
                except ValueError:
                    pass

            worksheet.write_string(xlsx_row, col, value)

    workbook.close()
