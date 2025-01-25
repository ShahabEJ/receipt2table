# Receipt to Table

A Pyton GUI application that:

1. Loads a receipt image.
2. Extracts text from the image (via **Tesseract**).
3. Sends the text to **OpenAI GPT** for structured parsing into items and total.
4. Displays the parsed data in a table.
5. Exports the table to a `.xlsx` Excel file.

This project contains three modules:

- **[main.py](./main.py):**  
  Contains all **GUI** logic for PySide6 (widgets, layouts, signals, etc.).
- **[services.py](./services.py):**  
  Contains **business logic**:
  - Tesseract OCR extraction
  - OpenAI GPT function-calling request
- **[excel_exporter.py](./excel_exporter.py):**  
  One function to **export** a `QTableWidget` to `.xlsx` using [XlsxWriter](https://github.com/JonathanSalwan/Capstone).

---

## Features

- **Image Loading**  
  Opens a file dialog to let the user pick any standard image format (PNG, JPEG, etc.).

- **Receipt Parsing**  
  - Uses [pytesseract](https://github.com/madmaze/pytesseract) + [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) to convert the image to raw text.
  - Sends the raw text to GPT-4o with **function calling**, instructing it to produce structured JSON containing:
    - A list of purchase `items` (with `description`, `quantity`, and `price`).
    - A final `total`.

- **Table Display**  
  - Results are shown in a `QTableWidget`.
  - The last row displays the total price.

- **Excel Export**  
  - Prompts the user for a file name and writes the table to an `.xlsx`.

---

## Setup

### 1. Clone / Download

```bash
git clone https://github.com/yourusername/receipt-to-table.git
cd receipt-to-table
```

### 2. Install Dependencies

Tested on **Python 3.11**:

```bash
pip install -r requirements.txt
```

### 3. Configure Tesseract

Ensure Tesseract is installed and accessible. For Windows, you might install Tesseract from [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) or from the [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki).

If Tesseract is installed in a non-default path, set the environment variable:

```bash
export TESSERACT_PATH="C:/Program Files/Tesseract-OCR/tesseract.exe"
```

### 4. Set your OpenAI API Key in the `.env` file:
OPENAI_API_KEY="sk-xxxxx"

## Run the App
1. Go to the `src` folder.
2. Run the app by `python main.py`.
