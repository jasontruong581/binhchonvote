from __future__ import annotations

import sys
import traceback

from app.main import main


def _pause_if_needed() -> None:
    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        try:
            input("Nhan Enter de thoat...")
        except EOFError:
            pass


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        print("Ung dung gap loi va khong the tiep tuc.")
        traceback.print_exc()
        _pause_if_needed()
        raise SystemExit(1)
