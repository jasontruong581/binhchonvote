from __future__ import annotations

from .base import SiteFlowContext


def wait_for_manual_checkpoint(*, context: SiteFlowContext, instruction: str) -> None:
    context.logger.info("Manual checkpoint required: %s", instruction)
    print()
    print("=== MANUAL CHECKPOINT ===")
    print(instruction)
    input("Hoan tat buoc thu cong roi nhan Enter de tiep tuc...")
