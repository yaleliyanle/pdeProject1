# Submission slides

`Financial_SDE_Submission_Slides.pdf` is the single presentation PDF. It contains
15 timed main slides, followed by four explicitly labelled Q&A backup slides.
The main presentation is designed for approximately 10 minutes. The attached
submission checklist specifies 10 minutes plus 3 minutes of Q&A, which replaces
the earlier 12-minute rehearsal target.

`Financial_SDE_Submission_Slides.tex` is a compact revision of the latest
48-page user-supplied deck. The original deck has not been overwritten.
`NOTES_EN.md` contains page-specific, simple-English speaker notes and suggested
timings. Do not read every displayed number or formula aloud.

The assigned team number is not known. Replace `\TeamNumber` in the TeX source
with the confirmed number and compile before uploading. Member names and IDs
are copied from the latest user-supplied deck; no individual contribution or
role is inferred.

All plot assets are vector PDFs stored under `assets/`, so this source folder
is self-contained. They use the same experiment outputs as the submission
report. No image is extracted from a screenshot.

Compile, with a TeX distribution that includes Beamer:

```sh
cd submission/slides
tectonic --keep-logs Financial_SDE_Submission_Slides.tex
```

Only the PDF is required for the presentation upload. The source and notes are
supplied for correction and rehearsal. The bibliography/Q&A pages are outside
the nominal main-talk timing.
