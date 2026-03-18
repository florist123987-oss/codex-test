class CollectionError(Exception):
    """Base error for article collection module."""


class FetchError(CollectionError):
    """Raised when target url cannot be fetched."""


class ParseError(CollectionError):
    """Raised when article content cannot be parsed from the html."""


class PersistenceError(CollectionError):
    """Raised when database save fails."""
