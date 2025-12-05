# -*- coding: utf-8 -*-
"""
This script implements the Flask backend server for the YourBudgetFriend web interface.

It handles:
- Serving the static user interface files (ybfui.html + static resources).
- Providing an API endpoint (`/run-crawler`) to trigger the web crawling process on demand.
- Returning success or error messages from the crawler back to the frontend.
- Automatically opening the web UI in a browser when the server starts.
"""

from flask import Flask, jsonify
import subprocess
import os
import webbrowser
from threading import Timer


app = Flask(
    __name__,
    static_folder='crawler/UI',     # Folder containing HTML and JSON UI files
    static_url_path=''              # Serve static files directly at the root URL ("/")
)

@app.route("/run-crawler", methods=["GET"])
def run_crawler():
    """
    API endpoint triggered by the UI button to execute the web crawler.
    Safely locates and runs the 'main.py' crawler script using a subprocess.
    """
    try:
        # Construct the full path to the crawler script.
        script_path = os.path.join(os.getcwd(), "crawler", "main.py")

        # Verify that the crawler script exists to prevent silent failures.
        if not os.path.exists(script_path):
            return jsonify({
                "status": "error",
                "message": f"Crawler script not found at: {script_path}"
            }), 500

        # Execute the crawler script as a subprocess and wait for its completion.
        # `capture_output=True` allows reporting stdout/stderr back to the UI for debugging.
        result = subprocess.run(["python", script_path], capture_output=True, text=True)

        if result.returncode == 0:
            # If the crawler exits successfully, return a success message.
            return jsonify({
                "status": "success",
                "message": "Crawler finished successfully."
            })
        else:
            # If the crawler fails, return an error message along with stdout/stderr for debugging.
            return jsonify({
                "status": "error",
                "message": f"Crawler failed: {result.stderr}",
                "stdout": result.stdout
            }), 500

    except Exception as e:
        # Catch any unexpected server errors and return a generic error message.
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    def open_browser():
        """Opens the web UI in a new browser tab."""
        webbrowser.open_new("http://127.0.0.1:5000/ybfui.html")

    # Schedule the browser to open shortly after the Flask server starts.
    Timer(2, open_browser).start()

    # Run the Flask application on port 5000 in debug mode (set to False for production).
    app.run(port=5000, debug=False)
