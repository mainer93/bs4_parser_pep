class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ParserFindVersionException(Exception):
    """Вызывается, когда парсер не может найти список версий Python."""
    pass
