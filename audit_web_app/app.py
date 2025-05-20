from flask import Flask, render_template, request, redirect, flash, send_file
from io import BytesIO
import pandas as pd
import json
from openpyxl import load_workbook

app = Flask(__name__)
app.secret_key = 'secure-key'

SHEET_MAP = {
    "Null Hypothesis": ["work_instruction", "clause", "statistical_test", "p_value", "effect_size", "compliance"],
    "Material Evidence": ["work_instruction", "clause", "evidence_summary", "evidence_grade", "coverage"],
    "Gap Severity": ["work_instruction", "clause", "gap_severity", "gap_description"],
    "Longitudinal Tracking": ["work_instruction", "metric", "value", "longitudinal_notes"]
}

def create_excel_file():
    """Create a new Excel file in memory with empty sheets"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet, columns in SHEET_MAP.items():
            pd.DataFrame(columns=columns).to_excel(writer, sheet_name=sheet, index=False)
    output.seek(0)
    return output

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_data = request.form.get('json_input')
        try:
            print("Received JSON:", json_data)  # Debug line
            data = json.loads(json_data)
            
            # Debug: Print parsed data
            print("Parsed data:", data)
            
            output = create_excel_file()
            book = load_workbook(output)
            writer = pd.ExcelWriter(output, engine='openpyxl', mode='a', if_sheet_exists='overlay')
            writer.book = book

            for sheet, columns in SHEET_MAP.items():
                if sheet not in data:
                    print(f"Skipping {sheet}, not in data")  # Debug
                    continue

                print(f"Processing {sheet}...")  # Debug
                df_new = pd.DataFrame(data[sheet])
                df_new = df_new[columns]

                if sheet in book.sheetnames:
                    df_existing = pd.read_excel(output, sheet_name=sheet)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined.to_excel(writer, sheet_name=sheet, index=False)
                else:
                    df_new.to_excel(writer, sheet_name=sheet, index=False)

            writer.save()
            output.seek(0)
            
            print("Excel generation successful!")  # Debug
            return send_file(
                output,
                as_attachment=True,
                download_name="audit_data.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            print("ERROR:", str(e))  # Debug
            flash(f"Server error: {str(e)}", 'error')
            return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
