class MlcaUserError(Exception):
    """A recoverable error suitable for display to the user."""


class IntegrityError(MlcaUserError):
    """Persisted evidence no longer matches its recorded state."""


class BudgetError(MlcaUserError):
    """A configured request budget would be exceeded."""
