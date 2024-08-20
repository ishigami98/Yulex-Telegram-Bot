class Todo:
    def __init__(self, title, user):
        self.title = title
        self.user = user
        self.is_completed = False

    def set_completed(self):
        self.is_completed = True

    def __str__(self):
        status = '✅' if self.is_completed else '🔴'
        return f"{status} {self.title}"