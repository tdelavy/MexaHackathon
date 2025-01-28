import os
import platform
import subprocess

# Get the absolute path of the current directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Change directory to the project folder
os.chdir(project_dir)

# Install dependencies
print("Installing required packages...")
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

# Run Streamlit app
print("Starting Streamlit app...")
subprocess.run(["streamlit", "run", "Gemini.py"], check=True)