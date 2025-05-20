from flask import Flask, render_template, request, send_file, flash
import pandas as pd
import json
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secure-key'

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

            # Create workbook in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, columns in SHEET_MAP.items():
                    if sheet_name in data:
                        df = pd.DataFrame(data[sheet_name])
                        df = df[[col for col in columns if col in df.columns]]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()
                output.seek(0)

            return send_file(
                output,
                as_attachment=True,
                download_name='audit_data.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except json.JSONDecodeError:
            flash("Invalid JSON format. Please check your input.", 'error')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')

    return render_template('index.html')
