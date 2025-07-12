"""
Launch script for BLISS web interface
Run this from the project root directory
"""
import subprocess
import sys
import os


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(project_root, 'web', 'components', 'app.py') 

    if not os.path.exists(app_path):
        print(f"Error: Streamlit app file not found at {app_path}")
        return
    

    print("Starting BLISS web interface...")
    print(f"App path: {app_path}")
    print("Open your browser to http://localhost:8501")
    print("Press Ctrl+C to stop the server")

    try:
        # Run Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], cwd=project_root)
    except KeyboardInterrupt:
        print("\nShutting down BLISS web interface...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")


if __name__ == "__main__":
    main()