from zope.interface import Interface


class IDepositBox(Interface):

    def put(value, token):
        """Put value plus token in box and return generated id.

        token may be optional.
        """

    def edit(secret, value, token):
        """Edit value in the box, when secret and token match.
        """

    def get(secret, token):
        """Get value from box, matching secret and token.

        token may be optional.
        """

    def pop(secret, token):
        """Pop value from box, matching secret and token.

        token may be optional.
        """
