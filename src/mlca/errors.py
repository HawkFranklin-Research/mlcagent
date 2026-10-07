class MlcaUserError(Exception):
    """A recoverable error with a category assigned where it originates."""

    def __init__(self, message, *, category=None):
        super().__init__(message)
        self.category = category or "runtime_error:" + type(self).__name__


class IntegrityError(MlcaUserError):
    """Persisted evidence no longer matches its recorded state."""


class BudgetError(MlcaUserError):
    """A configured model request budget would be exceeded."""

    def __init__(self, message):
        super().__init__(message, category="budget_stop")
