from __future__ import annotations

from pathlib import Path
from typing import Callable

import structlog

from ...config import Settings

logger = structlog.get_logger()


def resolve_assets_dir(settings: Settings) -> Path:
    base = Path(settings.telegram_assets_dir)
    if not base.is_absolute():
        base = (Path.cwd() / base).resolve()
    return base


def get_asset_path(settings: Settings, name: str) -> Path:
    assets_dir = resolve_assets_dir(settings)
    path = assets_dir / name
    if not path.exists():
        logger.warning("telegram_asset_missing", path=str(path))
    return path
