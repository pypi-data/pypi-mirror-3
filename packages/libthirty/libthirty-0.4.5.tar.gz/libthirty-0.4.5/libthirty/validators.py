from docar.exceptions import ValidationError


def naming(value):
    import re
    p = re.compile('^[a-z0-9_]+$')
    if not p.match(value):
        raise ValidationError("String invalid. May contain [a-z0-9_].")


def naming_with_dashes(value):
    import re
    p = re.compile('^[a-z0-9_-]+$')
    if not p.match(value):
        raise ValidationError("String invalid. May contain [a-z0-9_-].")


def max_25_chars(value):
    """Validate that valuew is not longer than 25 characters."""
    if len(value) >= 25:
        raise ValidationError(
                "String too long. A maximum of 25 characters allowed")
