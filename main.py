from flask import Flask, request, jsonify
import math
from fractions import Fraction

# 1. YOU MUST DEFINE 'app' FIRST
app = Flask(__name__)

# 2. THEN YOU CAN USE '@app.route'
@app.route('/')
def home():
    return "Math Solver API is Online!"

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        logic_code = data.get('logic', '')
        
        # Using the smarter variable loading we discussed
        variables = data.get('variables', {})
        combined_scope = {**data, **variables} 
        
        local_scope = combined_scope.copy()
        local_scope['math'] = math
        local_scope['Fraction'] = Fraction

        definition = "def solver():\n"
        for line in logic_code.split('\n'):
            definition += f"    {line}\n"
            
        exec(definition, {}, local_scope)
        result = local_scope['solver']()
        
        return jsonify({"result": str(result), "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "received_data": data}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
