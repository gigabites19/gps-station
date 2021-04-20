from re import Match
from .exceptions import AttributeNotSet


class BaseProtocol:
    """
    Base class that all the other protocols should inherit from.

    All subclasses should define attributes that will be sent to the server with
    one preceding underscore (_). If attribute requires any further processing after
    getting it from regex group, then it should be defined as a @property, the property
    name should also start with an underscode.

    :param required_sublass_attributes: Attributes that subclasses must define
    :type required_sublass_attributes: list
    """

    required_subclass_attributes: list = ['_protocol']

    def __init__(self, regex_match: Match) -> None:
        """
        Initializes the base parameters and checks that the subclass' instance and thus
        the subclass itself has defined required attributes.

        :param regex_match: re.Match object provided by the matcher, contains groups
        :type regex_match: Match
        :rtype: None
        """
        self.regex_match = regex_match

        self.check_subclass_attributes()

    def check_subclass_attributes(self) -> None:
        """
        Checks that the instance's class has defined all the required attributes

        :raises AttributeNotSet: In case one of the required attributes is not defined
        :rtype: None
        """
        for attribute in self.required_subclass_attributes:
            try:
                getattr(self, attribute)
            except AttributeError:
                raise AttributeNotSet(attribute)

    @property
    def payload(self) -> dict:
        """
        Returns a dictionary containing all the attributes the server needs to save GPS data.

        Loops over all the attributes/methods/class attributes and grabs those that starts with _ and guards against
        those that start with __ to avoid getting python's built-in stuff. We remove the leading  underscore because
        attribute names that we send from here must exactly match those defined in backend models.

        :returns: Cleaned, formatted data ready to be saved by the backend server.
        :rtype: dict
        """
        payload = {
            attr[1:]:getattr(self, attr) for attr in dir(self)
            if attr.startswith('_') and not attr.startswith('__')
        }

        return payload
