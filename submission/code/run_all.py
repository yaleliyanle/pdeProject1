"""Regenerate all experiments, independent checks, report tables, and figures.

The default reproduces production path counts. --smoke uses fewer paths in a
separate temporary artifact directory and is only an execution test.
"""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tempfile

CODE = Path(__file__).resolve().parent
PROJECT = CODE.parent if CODE.name == "code" else CODE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true",
                        help="Small end-to-end test; does not validate convergence orders")
    parser.add_argument("--output-dir",type=Path,
                        help="Override artifact root; production default is the package root")
    args = parser.parse_args()
    if args.output_dir is not None:
        output = args.output_dir.resolve()
    elif args.smoke:
        output = Path(tempfile.mkdtemp(prefix="financial-sde-smoke-"))
    else:
        output = Path(os.environ.get("FINANCIAL_SDE_OUTPUT_DIR", PROJECT)).resolve()
    if args.smoke and output == PROJECT.resolve():
        parser.error("--smoke must not overwrite the production package artifacts")
    output.mkdir(parents=True,exist_ok=True)
    env = os.environ.copy()
    env["FINANCIAL_SDE_OUTPUT_DIR"] = str(output)
    commands = [
        ("gbm.py", ["--paths","512","--pilot-paths","256","--batch-size","128"]
                   if args.smoke else []),
        ("nonaffine.py", ["--paths","512","--batch-size","128"] if args.smoke else []),
        ("verify.py", []),
    ]
    if (CODE/"submission_experiments.py").exists():
        extra = ["--repeats","2","--gbm-paths","512","--gbm-pilot-paths","128",
                 "--nonaffine-paths","128","--nonaffine-batch-size","64",
                 "--timing-paths","512","--timing-repeats","5"] if args.smoke else []
        commands.append(("submission_experiments.py", ["--output-dir",str(output)]+extra))
    commands.append(("build_report_data.py", []))
    for script, extra in commands:
        print(f"\nRunning {script}",flush=True)
        subprocess.run([sys.executable,str(CODE/script),*extra],cwd=PROJECT,env=env,check=True)
    mode = "SMOKE TEST (not production evidence)" if args.smoke else "Production reproduction"
    print(f"\n{mode} complete. Artifacts: {output}")
    print("Compile the report LaTeX source separately to refresh its PDF.")


if __name__ == "__main__":
    main()

