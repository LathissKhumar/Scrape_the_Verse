import sys
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent
_repo_root = _pkg_root.parent
for _path in (str(_pkg_root), str(_repo_root)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import uvicorn

from leadfinder.config.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("leadfinder.main:app", host="0.0.0.0", port=8000, reload=True)
