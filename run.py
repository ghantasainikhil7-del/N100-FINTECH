"""One-Click Platform Runner.
Execute with: python run.py
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    streamlit_exe = root / "venv" / "Scripts" / "streamlit.exe"
    
    # Use venv streamlit if available, else fallback to system streamlit
    if streamlit_exe.exists():
        cmd = [str(streamlit_exe), "run", str(root / "app.py")]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", str(root / "app.py")]
    
    print("=" * 60)
    print("🏛️  N100 Financial Intelligence Platform")
    print("=" * 60)
    print("Launching Streamlit Dashboard...")
    print("Local URL: http://localhost:8501")
    print("=" * 60)
    
    try:
        env = {**os.environ, "PYTHONPATH": str(root)}
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nPlatform stopped.")

if __name__ == "__main__":
    main()
