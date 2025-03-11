# api_server.py
from flask import Flask, request, jsonify
import seleniumInputGenerator  # your second code module

app = Flask(__name__)

@app.route('/process-rule-json', methods=['POST'])
def process_rule_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        output_file = "output.json"  # Optional, if your function needs it
        final_output = seleniumInputGenerator.main(data, output_file)

        return jsonify(final_output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)