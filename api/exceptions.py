class DatabaseInsertionError(Exception):
    """Exception raised when a database insertion fails."""
    pass

class MissingEnvironmentVariableError(Exception):
    """Exception raised when an environment variable is missing."""
    pass

