from re import Match
from .exceptions import AttributeNotSet


class BaseProtocol:
    """
    Base class that all the other protocols should inherit from.

    All subclasses should define attributes that will be sent to the server with
    one preceding underscore (_). If attribute requires any further processing after
    getting it from regex group, then it should be defined as a @property, the property
    name should also start with an underscore.

    :param required_sublass_attributes: Attributes that subclasses must define
    :type required_sublass_attributes: list
    """

    required_subclass_attributes: list = ['_protocol', 'regular_expressions']

    def __init__(self) -> None:
        """
        Initializes the base parameters and checks that the subclass' instance and thus
        the subclass itself has defined required attributes.

        :rtype: None
        """
        self.check_subclass_attributes()

    # TODO: test that this is always enforced
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
