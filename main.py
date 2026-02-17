from flask import Flask, request, jsonify
import math
from fractions import Fraction

app = Flask(__name__)

@app.route('/')
def home():
    return "Math Solver API is Online!"

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        logic_code = data.get('logic', '')
        variables = data.get('variables', {})

        local_scope = variables.copy()
        local_scope['math'] = math
        local_scope['Fraction'] = Fraction

        definition = "def solver():\n"
        for line in logic_code.split('\n'):
            definition += f"    {line}\n"
            
        exec(definition, {}, local_scope)
        result = local_scope['solver']()
        
        return jsonify({"result": str(result), "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
