from datetime import datetime, timezone

def aware_utcnow():
    return datetime.now(timezone.utc)


def aware_utcfromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)


def naive_utcnow():
    return aware_utcnow().replace(tzinfo=None)

def naive_utcfromtimestamp(timestamp):
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)


def select_string_with_substring(strings, substring):
    selected_strings = [s for s in strings if s.startswith(substring)]
    return selected_strings