# resume

A resume that builds like software: content lives in plain YAML/Markdown,
presentation lives in a LaTeX template, and a small Python script glues
them together into an ATS-friendly PDF (as many pages as the real content
honestly earns — currently 2, see "Visual design" below).

```
resume/
├── content/                 Source of truth — edit this
│   ├── personal.yaml         Name, contact info, links
│   ├── summary.md            Summary paragraph
│   ├── skills.yaml           Skill categories
│   ├── experience.yaml       Job history (supports tagging for variants)
│   ├── education.yaml        Education (currently empty — see file)
│   ├── projects.yaml         Projects (currently empty — see file)
│   └── variants.yaml         Optional — defines resume variants (see below)
│
├── templates/
│   └── resume.tex.jinja      LaTeX layout, driven by Jinja2 placeholders
│
├── scripts/
│   ├── build.py               Renders content → .tex, compiles → .pdf
│   └── build_all.py           Builds every variant in variants.yaml
│
├── output/                   Generated .tex/.pdf files (gitignored)
│
├── Makefile
├── .gitignore
└── .github/workflows/build-resume.yml
```

## Why this architecture (and what I simplified from the original proposal)

The original brief asked for structured YAML/Markdown content, a script to
generate the `.tex`, and build tooling — I kept all of that, because for a
resume you plan to maintain for years and eventually split into several
variants, that separation genuinely pays for itself: you'll edit
`experience.yaml` a lot and touch the LaTeX template rarely.

Where I simplified relative to the original proposal:

- **One template file, not a `templates/` directory of many.** A resume has
  one layout. A single `resume.tex.jinja` file is easier to reason about
  than several partials that must be assembled — that's complexity that
  would only pay off if the layout itself needed to vary section-by-section
  independently of content, which it doesn't here.
- **Variants are a data concern, not separate LaTeX files.** Rather than
  maintaining N `.tex` files (one per target role), each experience/project
  entry can carry `tags:`, and an optional `content/variants.yaml` maps a
  variant name to which tags to include. One template, one content set, N
  filtered builds. Adding a variant is a content edit, never a LaTeX edit.
  See "Creating Additional Resume Variants" below.
- **Jinja2 + PyYAML instead of a custom generator or a heavier static-site
  tool.** Both are mature, boring, widely known Python libraries — nothing
  clever, nothing hidden. `scripts/build.py` is ~100 lines and readable
  top to bottom in a few minutes five years from now.
- **No `resume/education.tex`-style per-section files.** Each content type
  (experience, education, skills, projects) is one YAML file; that's
  already the right granularity. Splitting further would add file-hopping
  without adding safety or clarity.

I did **not** simplify away structured content entirely (e.g. writing raw
LaTeX by hand) — with a 10+ year history and multiple planned variants, the
one-time cost of this setup is small compared to years of hand-editing
LaTeX tables every time a bullet changes.

## Visual design

The template deliberately stops short of copying "designed" resume
templates (multi-column skill grids, decorative skill-level ratings,
icon-only contact fields) even though they can look nicer — those are
exactly the things that break ATS and AI-tool text parsing: columns can
scramble reading order, dot/star ratings carry no extractable signal, and
icon-only fields can extract as garbage or nothing. Color, by contrast,
is purely a rendering attribute — it doesn't touch the underlying text
layer at all — so a restrained accent color is used for section headers,
the job/company line, and the name (see `MidnightBlue` in
`templates/resume.tex.jinja`) without any parsing risk.

Body text uses the `XCharter` font instead of LaTeX's Computer Modern
default, which reads as more "designed print document" and less "generic
LaTeX output." Fonts are always embedded and subsetted directly into the
PDF by `pdflatex`, so this renders identically on any machine regardless
of whether the viewer has the font installed — verified by inspecting the
PDF's embedded font objects, not just assumed.

Page length isn't fixed at one page. The template used to force everything
onto one page with tightly negative spacing; that constraint was removed
once experience content justified more room. A two-page resume gets
roughly 2.3x more callbacks than one-page for 10+ years of experience
(ResumeGo study), as long as the second page adds genuine substance.
`\Needspace` is used per job entry so an entry moves to the next page as a
whole rather than splitting a heading from its own bullets.

## Editing the resume

Almost all day-to-day edits happen in `content/`, never in `templates/`:

- **Contact info / links** → `content/personal.yaml`
- **Summary paragraph** → `content/summary.md`
- **Skills** → `content/skills.yaml` (add/reorder categories or items)
- **A new job, or a bullet change** → `content/experience.yaml`
- **Education** → `content/education.yaml` (currently empty; uncomment the
  example entry format in the file and fill it in)
- **Projects** → `content/projects.yaml` (currently empty; same pattern)

Content values are plain text — you don't need to escape LaTeX special
characters like `&`, `%`, or `_`; `scripts/build.py` escapes them
automatically before rendering.

You'd only touch `templates/resume.tex.jinja` if you want to change the
*layout* (fonts, spacing, section order at the structural level) rather
than the words on the page.

## Building locally

**Dependencies:**

- A LaTeX distribution providing `pdflatex` (e.g. TeX Live — on Debian/Ubuntu:
  `sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-lang-cyrillic && sudo mktexlsr`;
  on macOS: [MacTeX](https://www.tug.org/mactex/) includes everything needed).
  The last two packages provide the `XCharter` font used for body text —
  `texlive-lang-cyrillic` is only needed because `XCharter.sty` unconditionally
  requires Cyrillic encoding support even though the resume doesn't use it.
- Python 3.9+
- `pip install jinja2 pyyaml`

**Commands:**

```bash
make resume                  # builds content/*.yaml -> output/<Name>_Resume.pdf
make resume VARIANT=ruby     # builds a specific variant (see below)
make variants                # builds every variant defined in content/variants.yaml
make clean                   # removes generated files from output/
make watch                   # rebuilds automatically on file changes (needs `entr`)
```

Output lands in `output/<Name>_Resume.pdf` for the `general` variant, or
`output/<Name>_Resume_<Variant>.pdf` for any other variant — named after
`personal.yaml`'s `name` field rather than a generic "resume-general.pdf",
since a recognizable filename is less likely to get lost once it's one of
several files a recruiter has open or has downloaded.

## Editing in VS Code + LaTeX Workshop

This repo works fine with the [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
extension for live preview of the *generated* `.tex` file:

1. Run `make resume` once to generate the `.tex` file in `output/`.
2. Open that generated `.tex` file in VS Code with LaTeX Workshop installed;
   it will build/preview it directly like any other LaTeX file.
3. Remember the generated `.tex` file is disposable output, not the source —
   don't edit it directly, edit `content/` and re-run `make resume`.

If you want live preview while editing content, run `make watch` in a
terminal alongside your editor.

## Creating additional resume variants

The template renders whatever content it's given — variants are just
different *filtered slices* of the same content, not different LaTeX.

1. Add a `tags:` list to any entry in `experience.yaml` or `projects.yaml`
   that should be included only in specific variants. Entries with no
   `tags` field are included in every variant.

   ```yaml
   - company: Launchpad Recruits
     title: Software Engineer
     tags: [backend, ruby, rails, general]
     ...
   ```

2. Create (or edit) `content/variants.yaml` to define the variant names and
   which tags each one includes:

   ```yaml
   general:
     include_tags: null      # null = include everything, ignore tags

   ruby:
     include_tags: [ruby, rails, backend]

   leadership:
     include_tags: [leadership, mentoring]
   ```

3. Build it: `make resume VARIANT=ruby`, or build everything at once with
   `make variants`.

This keeps every variant working from the exact same underlying content —
there's only ever one place to fix a typo or add a job.

## How GitHub Actions works

`.github/workflows/build-resume.yml` runs on every push that touches
anything under `resume/`:

1. Checks out the repo and sets up Python.
2. Installs `jinja2` and `pyyaml`.
3. Installs a minimal TeX Live toolchain via `apt-get`.
4. Runs `scripts/build_all.py`, which builds every variant defined in
   `content/variants.yaml` (or just `general` if that file doesn't exist
   yet).
5. Uploads the resulting PDF(s) as a workflow artifact named `resume-pdfs`,
   downloadable from the Actions run summary. The build fails the job if
   compilation fails, so a broken resume can't silently merge.

PDFs aren't committed to git by default (see `.gitignore`) — they're
generated on demand locally or pulled from the latest Actions run. Delete
the two `output/*.pdf` lines in `.gitignore` if you'd rather commit them
directly.

## A couple of things worth knowing about the converted content

- The original PDF resume showed GitHub/LinkedIn usernames as icon labels
  without full URLs visible in the text layer. I filled in
  `https://github.com/<username>` and `https://linkedin.com/in/<username>`
  in `content/personal.yaml` as the standard URL pattern for those
  labels — worth a quick check that they're correct.
- The source resume had no Education or Projects sections, so
  `content/education.yaml` and `content/projects.yaml` are intentionally
  empty placeholders (the template just omits those sections when empty).
  Fill them in whenever you're ready.
- Wording was preserved as-is from the original PDF; nothing was rewritten
  or embellished.
