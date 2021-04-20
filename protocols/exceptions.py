class AttributeNotSet(Exception):

    def __init__(self, attribute: str):
        self.message = "Every subclass needs to possess '{}' attribute!".format(attribute)
        super().__init__(self.message)
