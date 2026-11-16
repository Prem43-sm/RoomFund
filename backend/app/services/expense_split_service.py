"""Expense split engine.

All monetary values are handled as integer minor units (paise) to avoid
floating-point errors. Rounding remainders are assigned deterministically.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


def split_equal(total_minor: int, participants: List[str]) -> List[Dict[str, Any]]:
    """Split total equally among participants.

    The remainder is assigned to the first participant deterministically.
    """
    n = len(participants)
    if n == 0:
        raise ValueError("At least one participant is required")
    base = total_minor // n
    remainder = total_minor % n
    results = []
    for i, user_id in enumerate(participants):
        share = base + (remainder if i == 0 else 0)
        results.append({"user_id": user_id, "share_amount_minor": share})
    return results


def split_percentage(
    total_minor: int, allocations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Split by percentage. allocations: [{user_id, percentage}]."""
    total_pct = sum(a["percentage"] for a in allocations)
    if abs(total_pct - 100.0) > 1e-9:
        raise ValueError("Percentages must total exactly 100%")

    results = []
    remaining = total_minor
    for i, alloc in enumerate(allocations):
        pct = Decimal(str(alloc["percentage"]))
        share = int((Decimal(total_minor) * pct / Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if i == len(allocations) - 1:
            share = remaining  # last participant gets the remainder
        remaining -= share
        results.append({"user_id": alloc["user_id"], "share_amount_minor": share})
    return results


def split_custom(
    total_minor: int, allocations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Split by custom amounts. allocations: [{user_id, share_amount_minor}]."""
    total_allocated = sum(a["share_amount_minor"] for a in allocations)
    if total_allocated != total_minor:
        raise ValueError("Custom share amounts must equal the expense total")
    return [{"user_id": a["user_id"], "share_amount_minor": a["share_amount_minor"]} for a in allocations]


def split_shares(
    total_minor: int, allocations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Split by shares/units. allocations: [{user_id, shares}]."""
    total_shares = sum(Decimal(str(a["shares"])) for a in allocations)
    if total_shares <= 0:
        raise ValueError("Total shares must be greater than zero")

    results = []
    remaining = total_minor
    for i, alloc in enumerate(allocations):
        share_dec = Decimal(str(alloc["shares"])) / total_shares * Decimal(total_minor)
        share = int(share_dec.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if i == len(allocations) - 1:
            share = remaining
        remaining -= share
        results.append({"user_id": alloc["user_id"], "share_amount_minor": share})
    return results


def compute_split(
    total_minor: int,
    split_method: str,
    participants: List[str],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Dispatch to the appropriate split method."""
    if split_method == "EQUAL":
        return split_equal(total_minor, participants)
    if split_method == "PERCENTAGE":
        return split_percentage(total_minor, config["allocations"])
    if split_method == "CUSTOM":
        return split_custom(total_minor, config["allocations"])
    if split_method == "SHARES":
        return split_shares(total_minor, config["allocations"])
    raise ValueError(f"Unknown split method: {split_method}")


def validate_participants(payer: str, participants: List[str]) -> None:
    """Validate that payer is among participants and list is non-empty."""
    if not participants:
        raise ValueError("At least one participant is required")
    if payer not in participants:
        raise ValueError("Payer must be a participant")