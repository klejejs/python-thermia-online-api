"""Download the public Thermia Online web app (online.thermia.se) for reading.

The site is a webpack single-page app: index.html, /api/configuration and every
JavaScript chunk are served without logging in. Only the register data behind
them needs an account. Run from the repository root:

    python scripts/fetch_thermia_web_app.py [output_dir]

Then search the bundles, e.g. for how register presentations are decoded:

    grep -o '.{0,200}isValueNameActiveBitmaskComparison.{0,200}' output_dir/*.js
"""

import json
import re
import sys
from pathlib import Path

import requests

BASE_URL = "https://online.thermia.se"
SCRIPT_TAG = re.compile(r'<script[^>]+src="/([^"]+\.js)"')
# The webpack runtime builds lazy chunk URLs as  e+"."+{123:"<hash>",...}[e]+".js"
JS_CHUNK_MAP = re.compile(r'\{((?:\d+:"[0-9a-f]+",?)+)\}\[e\]\+"\.js"')
CHUNK_HASH = re.compile(r'(\d+):"([0-9a-f]+)"')


def fetch(session: requests.Session, path: str) -> str:
    response = session.get(f"{BASE_URL}/{path}", timeout=(10, 60))
    response.raise_for_status()
    return response.text


def main() -> None:
    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".thermia-web")
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    index = fetch(session, "")
    (output_dir / "index.html").write_text(index)

    configuration = json.loads(fetch(session, "api/configuration"))
    (output_dir / "configuration.json").write_text(json.dumps(configuration, indent=2))

    entry_scripts = SCRIPT_TAG.findall(index)
    if not entry_scripts:
        sys.exit("No <script src> found in index.html; the site layout has changed.")

    files = set(entry_scripts)
    for script in entry_scripts:
        if script.startswith("manifest."):
            chunk_map = JS_CHUNK_MAP.search(fetch(session, script))
            if chunk_map is None:
                sys.exit(f"No JS chunk map found in {script}; the webpack runtime has changed.")
            files.update(f"{chunk}.{h}.js" for chunk, h in CHUNK_HASH.findall(chunk_map[1]))

    for name in sorted(files):
        (output_dir / name).write_text(fetch(session, name))

    print(f"Saved index.html, configuration.json and {len(files)} scripts to {output_dir}/")
    print(f"API base URL: {configuration.get('apiBaseUrl')}")


if __name__ == "__main__":
    main()
