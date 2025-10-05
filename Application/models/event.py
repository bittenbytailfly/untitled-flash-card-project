class Event:
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        """Use += to add a handler."""
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        """Use -= to remove a handler."""
        self.handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        """Call the event to fire it."""
        for handler in self.handlers:
            handler(*args, **kwargs)