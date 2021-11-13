class ProtocolNotRecognized(Exception):

    def __init__(self, data: str, message='Protocol was not recognized'):
        self.message = f'{message}: {data}'
        super().__init__(self.message)
