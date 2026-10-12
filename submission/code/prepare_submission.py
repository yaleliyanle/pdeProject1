"""Validate required artifacts and package the compiled report and code archive.

Preflight checks detect incomplete report fields and inputs newer than the PDF.
The output directory receives the report PDF, code ZIP, and checksum manifest.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "upload")
    args = parser.parse_args()
    report = ROOT / "report" / "report.pdf"
    for file in (report, ROOT / "README.md", ROOT / "requirements.txt"):
        if not file.is_file():
            parser.error("Missing required artifact: " + str(file))
    markers = ("NOT PROVIDED", "Not supplied", "Member to complete",
               "member to complete", "awaiting member completion")
    incomplete = []
    for file in (ROOT / "report").glob("*.tex"):
        if any(marker in file.read_text(encoding="utf-8") for marker in markers):
            incomplete.append(file.relative_to(ROOT).as_posix())
    report_inputs = (list((ROOT / "report").glob("*.tex")) +
                     list((ROOT / "results").glob("*.tex")) +
                     list((ROOT / "figures").glob("*.pdf")))
    for pdf, inputs in ((report, report_inputs),):
        newer = [p.relative_to(ROOT).as_posix() for p in inputs if p.is_file() and p.stat().st_mtime > pdf.stat().st_mtime]
        if newer:
            parser.error("Recompile " + pdf.relative_to(ROOT).as_posix() + "; newer inputs: " + ", ".join(newer))
    if incomplete:
        parser.error("Incomplete form content: " + ", ".join(incomplete))
    out = args.output_dir.resolve()
    protected = [ROOT / name for name in ("code", "tests", "report", "results", "figures", "source")]
    if out == ROOT or any(out == path or path in out.parents for path in protected):
        parser.error("Choose a dedicated output directory, not a source/artifact directory.")
    out.mkdir(parents=True, exist_ok=True)
    targets = [out / "Financial_SDE_Report.pdf", out / "Financial_SDE_Code.zip"]
    shutil.copy2(report, targets[0])
    exclude = {"__pycache__", ".venv", ".git", ".deps", "upload"}
    artifact_files = []
    for folder in ("code", "tests", "results", "figures", "report"):
        for file in (ROOT / folder).rglob("*"):
            if not file.is_file() or any(part in exclude for part in file.parts):
                continue
            if file.name == ".DS_Store" or file.suffix in {".pyc", ".aux", ".out", ".toc", ".nav", ".snm", ".vrb"}:
                continue
            if folder == "report" and file.parent == ROOT / folder and file.suffix in {".pdf", ".log"}:
                continue
            artifact_files.append(file)
    problem_pack = ROOT / "source" / "problem_pack.pdf"
    if problem_pack.is_file():
        artifact_files.append(problem_pack)
    artifact_files.extend(ROOT / name for name in ("README.md", "requirements.txt", ".gitignore", "numerical_summary.txt") if (ROOT / name).exists())
    with zipfile.ZipFile(targets[1], "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(artifact_files):
            archive.write(file, "Financial_SDE_Code/" + file.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(targets[1]) as archive:
        broken = archive.testzip()
        if broken is not None:
            raise RuntimeError("ZIP integrity failure: " + broken)
    manifest = {"team": 6, "status": "PACKAGED",
                "artifacts": [{"name": p.name, "bytes": p.stat().st_size,
                               "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in targets],
                "zip_files": len(artifact_files)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
