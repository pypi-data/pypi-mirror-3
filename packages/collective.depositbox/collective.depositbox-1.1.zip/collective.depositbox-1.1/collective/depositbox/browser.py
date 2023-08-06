from Acquisition import aq_inner
from Products.Five import BrowserView
from collective.depositbox.interfaces import IDepositBox


class DepositBoxView(BrowserView):
    """Simple browser view that knows how to interact with the deposit box.

    Simply a front end for the adapter really.
    """

    def put(self, value, token=None):
        context = aq_inner(self.context)
        box = IDepositBox(context)
        secret = box.put(value, token=token)
        return secret

    def confirm(self, secret, token=None):
        context = aq_inner(self.context)
        box = IDepositBox(context)
        confirmed = box.confirm(secret, token=token)
        return confirmed

    def get(self, secret, token=None):
        context = aq_inner(self.context)
        box = IDepositBox(context)
        stored = box.get(secret, token=token)
        return stored

    def pop(self, secret, token=None):
        context = aq_inner(self.context)
        box = IDepositBox(context)
        stored = box.pop(secret, token=token)
        return stored

    def edit(self, secret, value, token=None):
        context = aq_inner(self.context)
        box = IDepositBox(context)
        box.edit(secret, value, token=token)
