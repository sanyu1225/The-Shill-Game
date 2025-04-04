from datetime import datetime, timezone


def get_current_timestamp_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def from_now(time: datetime) -> str:
    now = get_current_time()
    # positive if future, negative if past
    delta = time - now
    seconds = int(delta.total_seconds())
    abs_seconds = abs(seconds)
    minutes = abs_seconds // 60
    hours = minutes // 60
    days = abs_seconds // 86400
    future = seconds > 0

    def suffix(s):
        return f"in {s}" if future else f"{s} ago"

    if abs_seconds <= 44:
        return suffix("a few seconds")
    elif abs_seconds <= 89:
        return suffix("a minute")
    elif abs_seconds <= 44 * 60:
        return suffix(f"{minutes} minutes")
    elif abs_seconds <= 89 * 60:
        return suffix("an hour")
    elif abs_seconds <= 21 * 3600:
        return suffix(f"{hours} hours")
    elif abs_seconds <= 35 * 3600:
        return suffix("a day")
    elif abs_seconds <= 25 * 86400:
        return suffix(f"{days} days")
    elif abs_seconds <= 45 * 86400:
        return suffix("a month")
    elif abs_seconds <= 319 * 86400:
        months = round(days / 30)
        return suffix(f"{months} months")
    elif abs_seconds <= 547 * 86400:
        return suffix("a year")
    else:
        years = round(days / 365)
        return suffix(f"{years} years")


if __name__ == "__main__":
    from datetime import timedelta

    now = get_current_time()
    print(now)

    few_seconds_ago = now - timedelta(seconds=5)
    print(from_now(few_seconds_ago))

    a_minute_ago = now - timedelta(minutes=1)
    print(from_now(a_minute_ago))

    four_hours_ago = now - timedelta(hours=4)
    print(from_now(four_hours_ago))

    two_days_ago = now - timedelta(days=2)
    print(from_now(two_days_ago))
