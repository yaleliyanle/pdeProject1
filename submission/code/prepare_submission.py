"""Build the three upload artifacts; refuse known human-completion gaps by default.

This is a packaging check, not authentication of signatures or contributions.
Run from the archive root after recompiling the reviewed report and slides.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-draft", action="store_true",
                        help="Create visibly DRAFT artifacts despite incomplete declarations")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "upload")
    args = parser.parse_args()
    report = ROOT / "report" / "report.pdf"
    slides = ROOT / "slides" / "Financial_SDE_Submission_Slides.pdf"
    for file in (report, slides, ROOT / "README.md", ROOT / "requirements.txt"):
        if not file.is_file():
            parser.error("Missing required artifact: " + str(file))
    markers = ("NOT PROVIDED", "Not supplied", "Member to complete",
               "member to complete", "awaiting member completion")
    gaps = []
    for file in (ROOT / "report").glob("*.tex"):
        if any(marker in file.read_text(encoding="utf-8") for marker in markers):
            gaps.append(file.relative_to(ROOT).as_posix())
    slide_source = ROOT / "slides" / "Financial_SDE_Submission_Slides.tex"
    text = slide_source.read_text(encoding="utf-8")
    team_number = re.search(r"\\newcommand\{\\TeamNumber\}\{([^}]+)\}", text)
    if "PENDING" in text or "NOT PROVIDED" in text or "Not provided" in text or (team_number and "pending" in team_number.group(1).lower()):
        gaps.append(slide_source.relative_to(ROOT).as_posix())
    report_inputs = list((ROOT / "report").glob("*.tex")) + list((ROOT / "results").glob("*.tex"))
    slide_inputs = [slide_source] + list((ROOT / "slides" / "assets").glob("*"))
    for pdf, inputs in ((report, report_inputs), (slides, slide_inputs)):
        newer = [p.relative_to(ROOT).as_posix() for p in inputs if p.is_file() and p.stat().st_mtime > pdf.stat().st_mtime]
        if newer:
            parser.error("Recompile " + pdf.relative_to(ROOT).as_posix() + "; newer inputs: " + ", ".join(newer))
    if gaps and not args.allow_draft:
        parser.error("Human completion still required: " + ", ".join(gaps) +
                     ". Complete declarations/recompile, or use --allow-draft for review only.")
    out = args.output_dir.resolve()
    if out == ROOT or ROOT in out.parents and out.name in {"code", "report", "slides", "results", "figures"}:
        parser.error("Choose a dedicated output directory, not a source/artifact directory.")
    out.mkdir(parents=True, exist_ok=True)
    suffix = "_DRAFT" if args.allow_draft else ""
    targets = [out / ("Financial_SDE_Report" + suffix + ".pdf"),
               out / ("Financial_SDE_Slides" + suffix + ".pdf"),
               out / ("Financial_SDE_Code" + suffix + ".zip")]
    shutil.copy2(report, targets[0])
    shutil.copy2(slides, targets[1])
    exclude = {"__pycache__", ".venv", ".git", ".deps", "upload"}
    artifact_files = []
    for folder in ("code", "tests", "results", "figures", "report", "slides", "compliance", "source"):
        for file in (ROOT / folder).rglob("*"):
            if not file.is_file() or any(part in exclude for part in file.parts):
                continue
            if file.name == ".DS_Store" or file.suffix in {".pyc", ".aux", ".out", ".toc", ".nav", ".snm", ".vrb"}:
                continue
            if folder in {"report", "slides"} and file.parent == ROOT / folder and file.suffix in {".pdf", ".log"}:
                continue
            artifact_files.append(file)
    artifact_files.extend(ROOT / name for name in ("README.md", "requirements.txt", ".gitignore", "numerical_summary.txt") if (ROOT / name).exists())
    with zipfile.ZipFile(targets[2], "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(artifact_files):
            archive.write(file, "Financial_SDE_Code/" + file.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(targets[2]) as archive:
        broken = archive.testzip()
        if broken is not None:
            raise RuntimeError("ZIP integrity failure: " + broken)
    manifest = {"status": "DRAFT_NOT_READY_FOR_UPLOAD" if args.allow_draft else "PACKAGED_REQUIRES_HUMAN_APPROVAL",
                "human_completion_files": gaps,
                "note": "Automated packaging does not verify personal declarations, signatures, or presentation rehearsal.",
                "artifacts": [{"name": p.name, "bytes": p.stat().st_size,
                               "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in targets],
                "zip_files": len(artifact_files)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
