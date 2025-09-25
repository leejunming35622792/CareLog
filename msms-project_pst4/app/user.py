class User:
    """A base class for all users in the system."""
    def __init__(self, username, password, user_id, name):
        self.username = username
        self.password = password
        self.id = user_id
        self.name = name
