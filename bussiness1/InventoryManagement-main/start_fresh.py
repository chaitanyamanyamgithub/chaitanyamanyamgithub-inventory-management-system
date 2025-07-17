from app import app
import os

# Clear any session files if they exist
session_path = app.instance_path
if os.path.exists(session_path):
    import shutil
    for file in os.listdir(session_path):
        if file.startswith('flask_session'):
            try:
                os.remove(os.path.join(session_path, file))
                print(f"Removed session file: {file}")
            except:
                pass

print("Starting Flask application...")
print("Visit: http://localhost:8000")
print("Press Ctrl+C to stop")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
