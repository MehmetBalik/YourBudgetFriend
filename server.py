from flask import Flask, jsonify
import subprocess
import os
import webbrowser
from threading import Timer


# Flask backend server for the YourBudgetFriend web interface.

# 1. Serves the UI (ybfui.html + static resources).
# 2. Executes crawler on demand when user presses “Crawl New Data” in the UI.
# 3. Returns success or error messages back to the frontend.


app = Flask(
    __name__,
    static_folder='crawler/UI',     # Folder with HTML and JSON UI files
    static_url_path=''              # Serve static files at root URL ("/")
)

@app.route("/run-crawler", methods=["GET"])
def run_crawler():

    #API endpoint triggered by the UI button.
    #Safely locates and executes the crawler which is the main.py file using subprocess.


    try:
        # Construct path to crawler file
        script_path = os.path.join(os.getcwd(), "crawler", "main.py")

        if not os.path.exists(script_path):
            # Avoid silent failures
            return jsonify({
                "status": "error",
                "message": f"Crawler script not found at: {script_path}"
            }), 500

        # Execute crawler and wait crawling is done
        # capture_output=True reports errors to UI
        result = subprocess.run(["python", script_path], capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Crawler finished successfully."
            })
        else:
            # Return stdout and stderr for debugging
            return jsonify({
                "status": "error",
                "message": f"Crawler failed: {result.stderr}",
                "stdout": result.stdout
            }), 500

    except Exception as e:
        # Catch unexpected server errors to avoid any crashes
        return jsonify({"status": "error", "message": str(e)}), 500

#Automatically opens ui in a browser on launch.
#Runs Flask on localhost for safe local development.

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/ybfui.html")

    # Delay browser open slightly until server starts
    Timer(2, open_browser).start()

    app.run(port=5000, debug=False)
