@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        logic_code = data.get('logic', '')
        
        # SMARTER VARIABLE LOADING
        # First, try to get the nested 'variables' dictionary
        variables = data.get('variables', {})
        
        # If 'variables' was a string like "[object Object]", it might be empty.
        # So, we also pull everything from the top level of 'data' 
        # to make sure we don't miss 'a', 'b', etc.
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
        # This will now tell us EXACTLY what 'data' looked like if it fails
        return jsonify({"error": str(e), "received_data": data}), 400
