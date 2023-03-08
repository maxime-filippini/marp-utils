from __future__ import annotations

import subprocess

subprocess.check_call(
    [
        'marp',
        '--pdf',
        'build.md',
        '-o',
        'x.pdf',
        '--pdf-outlines',
        '--pdf-outlines.pages=false',
        '--html',
        '--allow-local-files',
    ],
)
