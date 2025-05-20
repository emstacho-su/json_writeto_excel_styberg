from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import json
from openpyxl import load_workbook
import os

app = Flask(__name__)
app.secret_key = 'secure-key'  # Required for flashing messages

# Save path to OneDrive (your provided path)
ONEDRIVE_PATH = r"C:\Users\estachowiak\OneDrive - styberg.com"
EXCEL_FILENAME = "audit_data.xlsx"
EXCEL_PATH = os.path.join(ONEDRIVE_PATH, EXCEL_FILENAME)

SHEET_MAP = {
    "Null Hypothesis": ["work_instruction", "clause", "statistical_test", "p_value", "effect_size", "compliance"],
    "Material Evidence": ["work_instruction", "clause", "evidence_summary", "evidence_grade", "coverage"],
    "Gap Severity": ["work_instruction", "clause", "gap_severity", "gap_description"],
    "Longitudinal Tracking": ["work_instruction", "metric", "value", "longitudinal_notes"]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_data = request.form.get('json_input')
        try:
            data = json.loads(json_data)

            if not os.path.exists(EXCEL_PATH):
                flash(f"Excel file not found at:\n{EXCEL_PATH}", 'error')
                return redirect('/')

            book = load_workbook(EXCEL_PATH)
            writer = pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='a', if_sheet_exists='overlay')
            writer.book = book

            for sheet, columns in SHEET_MAP.items():
                if sheet not in data:
                    continue

                df_new = pd.DataFrame(data[sheet])
                df_new = df_new[columns]

                if sheet in book.sheetnames:
                    df_existing = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_excel(writer, sheet_name=sheet, index=False)
                else:
                    df_new.to_excel(writer, sheet_name=sheet, index=False)

            writer.save()
            writer.close()
            flash("✅ Data successfully written to your OneDrive Excel file.", 'success')
        except json.JSONDecodeError:
            flash("Invalid JSON input. Please check your formatting.", 'error')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')

        return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
