from flask import Flask, render_template, request, flash, send_file
from io import BytesIO
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

SHEET_MAP = {
    "Null Hypothesis Testing": ["work_instruction", "clause", "statistical_test", 
                               "p_value", "effect_size", "compliance"],
    "Material Evidence": ["work_instruction", "clause", "evidence_summary", 
                         "evidence_grade", "coverage"],
    "Gap Analysis": ["work_instruction", "clause", "gap_severity", "gap_description"],
    "Longitudinal Tracking": ["work_instruction", "metric", "value", "longitudinal_notes"]
}

REQUIRED_COLUMNS = {
    "Null Hypothesis Testing": ["work_instruction", "clause", "compliance"],
    "Material Evidence": ["work_instruction", "clause", "evidence_grade"],
    "Gap Analysis": ["work_instruction", "clause", "gap_severity"],
    "Longitudinal Tracking": ["work_instruction", "metric", "value"]
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/processor', methods=['GET', 'POST'])
def processor():
    if request.method == 'POST':
        if not request.form.get('json_input'):
            flash("Please provide JSON input", 'error')
            return redirect(request.url)
            
        try:
            data = json.loads(request.form['json_input'])
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet, columns in SHEET_MAP.items():
                    df = pd.DataFrame(columns=columns)
                    if sheet in data and data[sheet]:
                        missing_cols = [col for col in REQUIRED_COLUMNS[sheet] 
                                      if col not in data[sheet][0]]
                        if missing_cols:
                            raise ValueError(f"Missing required columns in {sheet}: {', '.join(missing_cols)}")
                        
                        df = pd.DataFrame(data[sheet])[columns]
                        df.to_excel(writer, sheet_name=sheet, index=False)
            
            output.seek(0)
            return send_file(
                output,
                as_attachment=True,
                download_name="audit_report.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except json.JSONDecodeError:
            flash("Invalid JSON format. Please check your input.", 'error')
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            app.logger.error(f"Processing error: {str(e)}")
            flash("Server error during processing. Please try again.", 'error')

    return render_template('processor.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 10000))