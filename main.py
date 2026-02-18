from flask import Flask, request, jsonify
import math
from fractions import Fraction
import os

# 1. Define the Flask app FIRST to avoid NameErrors
app = Flask(__name__)

@app.route('/')
def home():
    return "Math Solver API is Online!"

@app.route('/solve', methods=['POST'])
def solve():
    try:
        # Get the JSON data sent from n8n
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received", "status": "error"}), 400

        logic_code = data.get('logic', '')
        
        # NEW: Get the raw question text (e.g., "Evaluate {a} + {b}")
        question_template = data.get('question_text', '')

        # Pull variables (a, b, c, etc.)
        variables = data.get('variables', {})
        if not isinstance(variables, dict):
            variables = {}

        # ---------------------------------------------------------
        # NEW FEATURE: Formatting the Question String in Python
        # ---------------------------------------------------------
        try:
            # Python's .format() automatically replaces {a} with the value of a, etc.
            # This handles ANY number of variables (a, b, c, x, y...)
            formatted_question = question_template.format(**variables)
        except Exception:
            # If formatting fails (e.g., a missing variable), return the original text
            formatted_question = question_template

        # Create a combined scope containing your math variables
        exec_globals = {**data, **variables}
        exec_globals['math'] = math
        exec_globals['Fraction'] = Fraction

        # Wrap the logic in a function to handle 'return' statements
        wrapper_code = "def solver():\n"
        for line in logic_code.split('\n'):
            wrapper_code += f"    {line}\n"
            
        # Execute the wrapper using exec_globals for both global and local scope
        exec(wrapper_code, exec_globals)
        
        # Run the newly created solver() function
        result = exec_globals['solver']()
        
        # Return result AND the clean, formatted question text
        return jsonify({
            "result": str(result), 
            "question": formatted_question,  # <--- The formatted string is sent back here!
            "status": "success"
        })

    except Exception as e:
        # If it fails, we return the error AND the data we received to help debug
        return jsonify({
            "error": str(e), 
            "status": "error",
            "received_data": data
        }), 400
import uuid
from weasyprint import HTML
import requests
from docx import Document

N8N_WEBHOOK = "https://example.com"

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        html = data.get("html")
        chat_id = data.get("chat_id")

        if not html:
            return jsonify({"error":"no html"}),400

        uid = str(uuid.uuid4())

        html_file = f"{uid}.html"
        pdf_file = f"{uid}.pdf"
        docx_file = f"{uid}.docx"

        # save html
        with open(html_file,"w",encoding="utf-8") as f:
            f.write(html)

        # PDF using weasyprint
        HTML(string=html).write_pdf(pdf_file)


        # WORD
        doc = Document()
        doc.add_paragraph(html)
        doc.save(docx_file)

        # send back to n8n webhook
        files = {
            "pdf": open(pdf_file,"rb"),
            "docx": open(docx_file,"rb")
        }

        requests.post(N8N_WEBHOOK, files=files, data={"chat_id":chat_id})

        return jsonify({"status":"sent back to n8n"})

    except Exception as e:
        return jsonify({"error":str(e)})

if __name__ == '__main__':
    # Render provides the port via an environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
