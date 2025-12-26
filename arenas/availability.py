from datetime import datetime
from django.utils import timezone
from bookings.models import Booking
from arenas.timeblocks import timedelta

def get_weekday(date_obj):
    """
    Python weekday:
    Monday = 0
    Sunday = 6
    """
    return date_obj.weekday()


def build_datetime(date_obj, time_obj, tz):
    """
    Combine date + time into a timezone-aware datetime.
    """
    dt = datetime.combine(date_obj, time_obj)
    return timezone.make_aware(dt, tz)


def get_daily_base_slots(court, date_obj):
    """
    Returns base availability slots for a court on a given date,
    derived ONLY from SlotTemplate.
    """
    weekday = get_weekday(date_obj)

    templates = court.slot_templates.filter(
        weekday=weekday,
        is_active=True
    )

    slots = []

    for tpl in templates:
        start_dt = build_datetime(
            date_obj,
            tpl.start_time,
            timezone.get_current_timezone()
        )
        end_dt = build_datetime(
            date_obj,
            tpl.end_time,
            timezone.get_current_timezone()
        )

        slots.append({
            "start": start_dt,
            "end": end_dt,
            "price": tpl.base_price,
        })

    return slots
def subtract_interval(slot_start, slot_end, busy_start, busy_end):
    """
    Given one open slot [slot_start, slot_end)
    and one busy interval [busy_start, busy_end),
    return remaining open pieces (0, 1, or 2 intervals).
    """
    # No overlap
    if busy_end <= slot_start or busy_start >= slot_end:
        return [(slot_start, slot_end)]

    # Busy fully covers slot
    if busy_start <= slot_start and busy_end >= slot_end:
        return []

    pieces = []

    # Left piece remains
    if busy_start > slot_start:
        pieces.append((slot_start, min(busy_start, slot_end)))

    # Right piece remains
    if busy_end < slot_end:
        pieces.append((max(busy_end, slot_start), slot_end))

    # Remove zero-length pieces
    pieces = [(s, e) for (s, e) in pieces if e > s]
    return pieces
def subtract_busy_from_slots(slots, busy_intervals):
    """
    slots: list of dicts like {'start': dt, 'end': dt, 'price': Decimal}
    busy_intervals: list of tuples (busy_start_dt, busy_end_dt)

    returns: new slots list after removing busy time.
    """
    result = []

    for slot in slots:
        current = [(slot["start"], slot["end"])]

        for (busy_start, busy_end) in busy_intervals:
            next_current = []
            for (s, e) in current:
                next_current.extend(subtract_interval(s, e, busy_start, busy_end))
            current = next_current

        # Convert back to slot dicts
        for (s, e) in current:
            result.append({"start": s, "end": e, "price": slot["price"]})

    # sort by start time
    result.sort(key=lambda x: x["start"])
    return result
def get_busy_intervals(court, day_start, day_end):
    """
    Returns a list of (start_dt, end_dt) for bookings that overlap the day window.
    Only counts RESERVED bookings.
    """
    qs = Booking.objects.filter(
        court=court,
        status=Booking.Status.RESERVED,
        start__lt=day_end,
        end__gt=day_start,
    ).order_by("start")

    return [(b.start, b.end) for b in qs]
def get_daily_available_slots(court, date_obj):
    base_slots = get_daily_base_slots(court, date_obj)

    if not base_slots:
        return []

    # day window = from first slot start to last slot end
    day_start = min(s["start"] for s in base_slots)
    day_end = max(s["end"] for s in base_slots)

    busy = get_busy_intervals(court, day_start, day_end)
    return subtract_busy_from_slots(base_slots, busy)
def split_into_blocks(slot_start, slot_end, block_minutes=90):
    """
    Split a time window into fixed blocks.
    """
    blocks = []
    current = slot_start
    delta = timedelta(minutes=block_minutes)

    while current + delta <= slot_end:
        blocks.append({
            "start": current,
            "end": current + delta,
        })
        current += delta

    return blocks
def get_daily_booking_blocks(court, date_obj, block_minutes=90):
    """
    Returns preset booking blocks that are:
    - within availability
    - not overlapping bookings
    """
    available_slots = get_daily_available_slots(court, date_obj)

    blocks = []
    for slot in available_slots:
        blocks.extend(
            split_into_blocks(
                slot["start"],
                slot["end"],
                block_minutes=block_minutes,
            )
        )

    return blocks
