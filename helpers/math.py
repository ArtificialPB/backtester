
def safe_round(value, digits):
    if value is not None:
        value = round(value, digits)
    return value
