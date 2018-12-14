from flask_login import current_user


def is_authenticated():
    return current_user.is_authenticated


def pretty_date(dt):
    """
    Args:
        dt Datetime object
    Returns:
        Pretty string representation of dt
    """
    return dt.strftime('%d %B %Y')
