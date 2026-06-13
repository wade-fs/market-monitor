# cache.py — JSON 檔案快取（TTL based）
import json, logging, time
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

logger = logging.getLogger(__name__)


class FileCache:
    """
    把每個 key 存成一個 JSON 檔，TTL 到期就視為 miss。
    路徑結構：{cache_dir}/{key}.json
    """

    def __init__(self, cache_dir: Path):
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace(":", "_")
        return self.dir / f"{safe}.json"

    def get(self, key: str, ttl_seconds: int) -> Optional[Any]:
        p = self._path(key)
        if not p.exists():
            return None
        try:
            age = time.time() - p.stat().st_mtime
            if age > ttl_seconds:
                return None
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Cache read {key}: {e}")
            return None

    def set(self, key: str, data: Any) -> bool:
        p = self._path(key)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"Cache write {key}: {e}")
            return False

    def delete(self, key: str):
        p = self._path(key)
        if p.exists():
            p.unlink()

    def list_keys(self) -> list:
        return [p.stem for p in self.dir.glob("*.json")]

    def stats(self) -> dict:
        files = list(self.dir.glob("*.json"))
        return {
            "total_keys": len(files),
            "total_size_kb": round(sum(f.stat().st_size for f in files) / 1024, 1),
            "keys": [f.stem for f in files],
        }
