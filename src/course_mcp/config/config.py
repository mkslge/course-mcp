from pathlib import Path
import os


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


def _get_root_dir() -> Path:
    project_root = Path(__file__).resolve().parents[3]
    _load_env_file(project_root / ".env")

    root_dir = os.environ.get("ROOT_DIR") or os.environ.get("ROOT_DIR_")
    if not root_dir:
        raise RuntimeError("Missing ROOT_DIR in .env or environment")

    path = Path(root_dir).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(f"ROOT_DIR does not exist: {path}")
    if not path.is_dir():
        raise RuntimeError(f"ROOT_DIR is not a directory: {path}")

    return path


ROOT_DIR = _get_root_dir()
