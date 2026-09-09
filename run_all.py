"""Reproduce the two full experiments, independent checks, and report inputs."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
for script in ("gbm.py","nonaffine.py","verify.py","build_report_data.py"):
    print(f"\nRunning {script}",flush=True)
    subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
print("\nExperiments complete. Compile the supplied LaTeX source twice to rebuild the PDF.")

