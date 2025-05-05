import os
import subprocess
from pathlib import Path

# Configure paths
PYTHON_EXEC = r"C:\Users\Me\AppData\Local\Programs\Python\Python311\python.exe"
LAMBDA_CONVERTER = r"C:\Users\Me\Desktop\Lambda Project\Lambda-Actions\LambdaC\lambdaC.py"
INPUT_DIR = r"C:\Users\Me\Desktop\Lambda Project\Lambda-Actions\Playbooks_Repo\xsoar"
OUTPUT_DIR = r"C:\Users\Me\Desktop\Lambda Project\Lambda-Actions\Playbooks_Repo\lambda"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Loop through all input files
playbook_files = list(Path(INPUT_DIR).glob("*.yml")) + list(Path(INPUT_DIR).glob("*.json"))
print(f"Found {len(playbook_files)} playbooks to convert.\n")

for idx, pb_file in enumerate(playbook_files, start=1):
    pb_name = pb_file.stem
    output_path = Path(OUTPUT_DIR) / f"{pb_name}.yml"

    if output_path.exists():
        print(f"⚠️  Skipping duplicate: {output_path}")
        continue

    print(f"[{idx}] Converting: {pb_file}")
    cmd = [
        PYTHON_EXEC,
        LAMBDA_CONVERTER,
        "--input-file", str(pb_file),
        "--input-vendor", "xsoar",
        "--output-vendor", "lambda",
        "--output-dir", OUTPUT_DIR,
        "--ai-fallback"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
