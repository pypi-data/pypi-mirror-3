def render_as_W3CDTF(date):
    """Renders the given date in a W3C Date and Time Format."""
    if callable(date): date = date()
    return date.toZone('UTC').strftime('%Y-%m-%dT%H:%M:%SZ')
