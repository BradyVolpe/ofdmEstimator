from flask import Flask, request, jsonify, send_file
from ofdm_estimation import estimate_ofdm_throughput
from ofdma_estimation import estimate_ofdma_throughput
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')  # serve index.html from root

@app.route('/api/estimate')
def estimate():
    try:
        channel_type = request.args.get('type', 'ofdm')
        spectrum = float(request.args.get('spectrum', 192))
        mod_order = float(request.args.get('modOrder', 12))
        spacing = float(request.args.get('spacing', 50))
        guard = float(request.args.get('guard', 2))
        exclude = float(request.args.get('exclude', 2))

        if channel_type == 'ofdm':
            throughput = estimate_ofdm_throughput(spectrum, mod_order, spacing, guard, exclude)
        else:
            throughput = estimate_ofdma_throughput(spectrum, mod_order, spacing, guard, exclude)

        return jsonify({'throughput': round(throughput, 3)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)