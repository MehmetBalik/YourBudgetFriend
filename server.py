from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route("/run-crawler", methods=["GET"])
def run_crawler():
    try:
        # Correct path to crawler main.py
        script_path = os.path.join(os.getcwd(), "crawler", "main.py")

        if not os.path.exists(script_path):
            return jsonify({
                "status": "error",
                "message": f"Crawler script not found at: {script_path}"
            }), 500

        # Launch the crawler
        subprocess.Popen(["python", script_path])

        return jsonify({"status": "success", "message": "Crawler started."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

