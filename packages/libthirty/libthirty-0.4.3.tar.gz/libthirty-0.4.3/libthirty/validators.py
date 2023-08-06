from docar.exceptions import ValidationError


def resource_name(value):
    import re
    p = re.compile('^[a-zA-Z0-9_.]+$')
    if not p.match(value):
        raise ValidationError("String invalid. May contain [a-zA-Z0-9_].")
