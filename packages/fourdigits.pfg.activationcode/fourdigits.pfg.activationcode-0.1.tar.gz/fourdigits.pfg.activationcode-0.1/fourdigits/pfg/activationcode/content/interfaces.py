from zope.interface import Interface


class IFormActivationCodeField(Interface):
    """Interface for activation Field.
    """

    def onSuccess(fields, REQUEST=None):
        """
        """
