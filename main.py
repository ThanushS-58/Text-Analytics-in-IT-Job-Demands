import subprocess
import sys
import os

os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
os.environ["STREAMLIT_SERVER_PORT"] = "5000"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "app.py",
    "--server.port", "5000",
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS=false",
    "--server.enableWebsocketCompression=false"
])
