if isinstance(value, dict):
    reason = str(value.get("reason", ""))
else:
    reason = str(value)
