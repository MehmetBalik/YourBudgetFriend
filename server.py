from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os
import webbrowser
from threading import Timer

app = Flask(__name__, static_folder='crawler/UI', static_url_path='')
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
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/ybfui.html")

    Timer(2, open_browser).start()
    app.run(port=5000, debug=True)