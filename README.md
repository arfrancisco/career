# career

A long-term, version-controlled home for everything related to my career
materials — treated as a small software project rather than a pile of
documents.

## Layout

```
career/
├── resume/           Resume content + LaTeX build system (implemented)
├── cover-letters/     Placeholder — see cover-letters/README.md
├── brag-document/      Placeholder — see brag-document/README.md
├── interview-notes/    Placeholder — see interview-notes/README.md
├── portfolio/           Placeholder — see portfolio/README.md
└── README.md
```

Only `resume/` is implemented so far. The other folders exist as
placeholders with a README describing their intended purpose, and will be
built out the same way: content separated from presentation, generated
output, checked into git.

See [`resume/README.md`](resume/README.md) for how the resume system works,
how to edit it, and how to build it.

## Original source resume

`archive/` contains the original PDF resume that `content/` was converted
from (as of the initial commit). It's kept for reference — to check wording
against the source, or roll back if a future edit strays too far — and
isn't used by the build in any way.
