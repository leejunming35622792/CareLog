class User:
    # Base Class for All Users
    def __init__(self, username, password, user_id, name):

        # Credentials for Login
        self.username = username
        self.password = password

        # Personal data
        self.id = user_id
        self.name = name
