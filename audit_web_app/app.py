from flask import Flask, render_template, request, redirect, flash, send_file
from io import BytesIO
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-fallback-key')

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
            
            # Create new Excel file in memory
            output = BytesIO()
            
            # Initialize writer with all sheets
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet, columns in SHEET_MAP.items():
                    # Create empty DataFrame for each sheet
                    df = pd.DataFrame(columns=columns)
                    if sheet in data:
                        # If we have data for this sheet, add it
                        new_data = pd.DataFrame(data[sheet])
                        # Ensure only expected columns are included
                        new_data = new_data[columns]
                        df = pd.concat([df, new_data], ignore_index=True)
                    df.to_excel(writer, sheet_name=sheet, index=False)
            
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name="audit_data.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except json.JSONDecodeError:
            flash("Invalid JSON input. Please check your formatting.", 'error')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')

        return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render's default port
    app.run(host='0.0.0.0', port=port)
