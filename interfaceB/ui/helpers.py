def format_duration(seconds):
    if seconds is None:
        return "N/A"
    total_seconds = int(round(seconds))
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        m, s = divmod(total_seconds, 60)
        return f"{m}m {s}s"
    else:
        h, r = divmod(total_seconds, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"
