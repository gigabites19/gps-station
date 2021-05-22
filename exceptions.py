class ProtocolNotRecognized(Exception):

    def __init__(self, message='Protocol was not recognized.'):
        self.message = message
        super().__init__(self.message)
