#!/usr/bin/env python3
"""Validate connectivity to every configured integration.

Run after setting your live credentials (and INTEGRATIONS_MOCK_MODE=false) to get
a green/red report before going live.

    backend/venv/Scripts/python scripts/check_integrations.py   # Windows
    backend/venv/bin/python scripts/check_integrations.py        # Linux/macOS
"""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.integrations.hub import get_integration_hub  # noqa: E402


async def main() -> int:
    status = await get_integration_hub().status()
    mode = "MOCK" if status["mock_mode"] else "LIVE"
    print(f"Integration mode: {mode}\n")
    worst = 0
    for check in status["integrations"]:
        ok = check.get("ok")
        mark = "[ OK ]" if ok else "[FAIL]"
        if not ok:
            worst = 1
        print(f"  {mark}  {check['name']:<11} ({check.get('mode', '?')})  {check.get('detail', '')}")
    print(f"\nOverall: {'all green' if status['all_ok'] else 'attention needed'}")
    return 0 if status["all_ok"] else worst


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
