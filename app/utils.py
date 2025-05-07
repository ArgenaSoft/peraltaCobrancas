from datetime import timedelta

def beautify_timedelta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours} hora{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minuto{'s' if minutes != 1 else ''}")
    if seconds and not hours:
        parts.append(f"{seconds} segundo{'s' if seconds != 1 else ''}")

    return " e ".join(parts)
