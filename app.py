from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ofdm_estimation import estimate_ofdm_throughput
from ofdma_estimation import estimate_ofdma_throughput

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/estimate', methods=['GET'])
def estimate():
    try:
        channel_type = request.args.get('type', 'ofdm')
        spectrum = float(request.args.get('spectrum', 192))
        mod_order = float(request.args.get('modOrder', 12))
        spacing = float(request.args.get('spacing', 50))
        guard = float(request.args.get('guard', 2))
        exclude = float(request.args.get('exclude', 2))

        print(f"Received params: type={channel_type}, spectrum={spectrum}, mod_order={mod_order}, spacing={spacing}, guard={guard}, exclude={exclude}")

        # Validate inputs
        if spectrum <= 0 or mod_order <= 0 or spacing <= 0:
            return jsonify({'error': 'Spectrum, modulation order, and spacing must be positive numbers.'}), 400

        if channel_type == 'ofdm':
            throughput = estimate_ofdm_throughput(spectrum, mod_order, spacing, guard, exclude)
        elif channel_type == 'ofdma':
            throughput = estimate_ofdma_throughput(spectrum, mod_order, spacing, guard, exclude)
        else:
            return jsonify({'error': f'Unsupported channel type: {channel_type}'}), 400

        print(f"Calculated throughput: {throughput}")

        return jsonify({'throughput': round(throughput, 3)})
    except Exception as e:
        print(f"Exception in estimate: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)