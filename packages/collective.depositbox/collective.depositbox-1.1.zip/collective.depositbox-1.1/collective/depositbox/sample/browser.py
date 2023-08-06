from collective.depositbox.browser import DepositBoxView


class BaseView(DepositBoxView):
    # These variables should be available to the template:
    secret = None
    token = None
    value = None
    stored = None

    # Which form input should be taken as the token? (None works too)
    token_id = 'email'
    # Which form inputs should be taken as value?  Can contain the
    # token_id as well.
    inputs = ['email', 'mytext']

    def __call__(self):
        # Get the secret, token and value, when known.
        self.secret = self.get_secret()
        self.token = self.get_token()
        self.value = self.get_value()

        # Do the add/edit/confirm/delete/whatever.  This may update
        # self.secret and have other side effects as well.
        self.update()

        # Render whatever was set as the template in zcml:
        return self.index()

    def get_token(self):
        return self.request.form.get(self.token_id)

    def get_secret(self):
        return self.request.form.get('secret', '')

    def get_value(self):
        form = dict()
        for input_id in self.inputs:
            value = self.request.form.get(input_id)
            if value is not None:
                form[input_id] = value
        return form


class Add(BaseView):

    def update(self):
        if self.token_id and not self.token:
            # Token is required.
            return
        if not self.value:
            return
        # Add the value (and token) and make the secret available on
        # the view.
        self.secret = self.put(self.value, token=self.token)
        return self.secret


class Confirm(BaseView):

    confirmed = False

    def update(self):
        """Confirm the item/token.
        """
        if not self.secret:
            return
        if self.token_id and not self.token:
            # Token is required.
            return

        self.confirmed = self.confirm(self.secret, token=self.token)
        self.stored = self.get(self.secret, token=self.token)


class Edit(BaseView):

    def update(self):
        """Change the stored value when there are changes.

        And get the stored value when there is nothing in the request.
        """
        if not self.secret:
            return
        if self.token_id and not self.token:
            # Token is required.
            return

        self.stored = self.get(self.secret, token=self.token)
        if not self.stored:
            return
        if not self.value:
            # for displaying
            self.value = self.stored
            return
        if self.value == self.stored:
            # No changes
            return
        # Store only changes: update the stored value, so we do not
        # lose any data when there is no corresponding key in the new
        # value.
        for key, value in self.stored.items():
            if key not in self.value.keys():
                self.value[key] = value

        # Check again for differences
        if self.value != self.stored:
            self.edit(self.secret, self.value, token=self.token)


class Delete(BaseView):

    deleted = False

    def update(self):
        """Delete the item/token.
        """
        if not self.secret:
            return
        if self.token_id and not self.token:
            # Token is required.
            return

        if self.request.form.get('delete'):
            self.stored = self.pop(self.secret, token=self.token)
            self.deleted = True
        else:
            self.stored = self.get(self.secret, token=self.token)
            if self.request.form.get('cancel'):
                self.request.RESPONSE.redirect(
                    self.context.absolute_url())
