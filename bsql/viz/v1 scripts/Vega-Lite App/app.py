import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    vega_lite_spec = request.form['vega_lite_spec']
    try:
        # Attempt to parse the Vega-Lite specification as JSON
        spec_json = json.loads(vega_lite_spec)
    except json.JSONDecodeError as e:
        return render_template('index.html', error="Invalid JSON format")

    return render_template('visualization.html', vega_lite_spec=json.dumps(spec_json))

@app.route('/get_vega_lite_spec')
def get_vega_lite_spec():
    # This route is for fetching the Vega-Lite spec on the visualization page
    return jsonify(json.loads(request.form['vega_lite_spec']))

if __name__ == '__main__':
    app.run(debug=True)
