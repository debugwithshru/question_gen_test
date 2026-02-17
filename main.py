from flask import Flask, request, jsonify
import math
from fractions import Fraction

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
        
        # Pull variables (a, b, c, etc.)
        # We also merge them with the top-level data as a backup
        variables = data.get('variables', {})
        if not isinstance(variables, dict):
            variables = {}
            
        # Create a combined scope containing your math variables
        # This ensures 'a' and 'b' are available to the script
        exec_globals = {**data, **variables}
        exec_globals['math'] = math
        exec_globals['Fraction'] = Fraction

        # Wrap the logic in a function to handle 'return' statements
        wrapper_code = "def solver():\n"
        for line in logic_code.split('\n'):
            wrapper_code += f"    {line}\n"
            
        # Execute the wrapper using exec_globals for both global and local scope
        # This is the "Magic" that fixes "name 'a' is not defined"
        exec(wrapper_code, exec_globals)
        
        # Run the newly created solver() function
        result = exec_globals['solver']()
        
        return jsonify({"result": str(result), "status": "success"})

    except Exception as e:
        # If it fails, we return the error AND the data we received to help debug
        return jsonify({
            "error": str(e), 
            "status": "error",
            "received_data": data
        }), 400

if __name__ == '__main__':
    # Render uses gunicorn, but this allows for local testing too
    app.run(host='0.0.0.0', port=8080)
