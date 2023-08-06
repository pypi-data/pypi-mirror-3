Tests
-----

We create box to keep values in:

    >>> from collective.depositbox.store import Box
    >>> box = Box()

We put some value in it and get a secret back:

    >>> secret = box.put(42)

Using the secret as a key, we can get our value back:

    >>> box.get(secret)
    42

We can put any object in the box:

    >>> value = object()
    >>> secret = box.put(value)
    >>> box.get(secret) is value
    True

The secret used to be an integer, but we switch to a string:

    >>> isinstance(secret, str)
    True

We can get the item multiple times, but we can also pop the item,
which means we really take the item out of the box:

    >>> box.get(secret) is value
    True
    >>> box.get(secret) is value
    True
    >>> box.pop(secret) is value
    True
    >>> box.pop(secret) is None
    True
    >>> box.get(secret) is None
    True

You can edit an item:

    >>> secret = box.put(object())
    >>> box.get(secret)
    <object object at ...>
    >>> box.edit(secret, 'I have been edited.')
    >>> box.pop(secret)
    'I have been edited.'

The secret is a random integer.  When a generated random key is
already taken (small chance, but still a chance), we simply try
again.  This can be tested by seeding the random generator.  First we
check what the first three secrets are that will be generated:

    >>> import random
    >>> random.seed(42)
    >>> first_secret = box._generate_new_id()
    >>> first_secret
    'wbkh9tzc'
    >>> second_secret = box._generate_new_id()
    >>> second_secret
    'pbhq8gs9'
    >>> third_secret = box._generate_new_id()
    >>> third_secret
    'jt3bzvkf'

We reset the random generator with the same seed and put an item in
the box:

    >>> random.seed(42)
    >>> box.put('first') == first_secret
    True

Reseed and put a second item in the box; since the first secret is
already taken, this gets stored under the second secret:

    >>> random.seed(42)
    >>> box.put('second') == second_secret
    True

Remove the first item:

    >>> box.pop(first_secret)
    'first'

Reseed and put two more items in the box; only the second secret is
already taken now, so the third item gets the first secret and the
fourth item gets the third secret:

    >>> random.seed(42)
    >>> box.put('third') == first_secret
    True
    >>> box.put('fourth') == third_secret
    True

We can optionally store an item with an extra token.  Then we can only
get the item back when we supply both the secret and the token.  This
provides extra safety.  We must first confirm the token though
(usually this will be an email address).

    >>> secret = box.put('my data', 'maurits@example.com')
    >>> box.get(secret, 'maurits@example.com') is None
    True
    >>> box.confirm(secret, 'maurits@example.com')
    True
    >>> box.get(secret, 'maurits@example.com')
    'my data'

Confirming wrong tokens does not help:

    >>> box.confirm(secret)
    >>> box.get(secret) is None
    True
    >>> box.confirm(secret, 'wrong token')
    >>> box.get(secret, 'wrong token') is None
    True

Removing the item also needs the token:

    >>> box.pop(secret)
    >>> box.pop(secret, 'maurits@example.com')
    'my data'

If we get None back, we always interpret this as meaning there was no
match.  So we should not accept None as a valid value to store in the
box:

    >>> box.put(None)
    Traceback (most recent call last):
    ValueError

Each unconfirmed item expires after a while.  Each time a new item is
put in the box, we check if it is time to do a purge; each day a purge
is done.  For an item to be purged, it has to be unconfirmed and it
must have exceeded its maximum age, which by default is 7 days.

We check how many items we have currently:

    >>> start_items = len(box.data)
    >>> start_items
    4

We can purge manually:

    >>> box.purge()
    >>> len(box.data) == start_items
    True

We modify the creation timestamp of the first item to be 7 days and a
few seconds in the past:

    >>> first_key = box.data.keys()[0]
    >>> first_item = box.data[first_key]
    >>> import time
    >>> first_item.timestamp = int(time.time()) - box.max_age * 86400 - 5

Confirmed items do not get purged:

    >>> first_item.confirmed = True
    >>> box.purge()
    >>> len(box.data) == start_items
    True

Unconfirmed items do get purged:

    >>> first_item.confirmed = False
    >>> box.purge()
    >>> len(box.data) == start_items - 1
    True

Like mentioned earlier, the purge also happens automatically when
adding an item, but at most once a day.

First we create a target for eliminating:

    >>> doomed_secret = box.put('doomed')
    >>> doomed = box.data.get(doomed_secret)
    >>> doomed.confirmed
    False
    >>> doomed.timestamp = int(time.time()) - box.max_age * 86400 - 5
    >>> len(box.data) == start_items
    True

This item should be eliminated, but only when the last purge was more
than 24 hourse ago:

    >>> secret = box.put('new')
    >>> len(box.data) == start_items + 1
    True
    >>> box.data.get(doomed_secret)
    <collective.depositbox.store.BoxItem object at ...>

We reset the last purge time; adding the next item should now delete
the doomed item:

    >>> box._last_purge = int(time.time()) - 86400 - 5
    >>> secret = box.put('even newer')
    >>> len(box.data) == start_items + 1
    True
    >>> box.data.get(doomed_secret) is None
    True

One more thing: when an item is supposed to be purged but the purge
code for the entire box is not called yet, getting the item will
actually remove it; in other words: you cannot get an outdated
unconfirmed item.

    >>> box.get(secret)
    'even newer'
    >>> len(box.data) == start_items + 1
    True
    >>> box.data.get(secret).timestamp = int(time.time()) - box.max_age * 86400 - 5
    >>> box.get(secret) is None
    True
    >>> len(box.data) == start_items
    True

We can get all confirmed data:

    >>> confirmed = box.get_all_confirmed()
    >>> confirmed
    <generator object ...>
    >>> sorted([x for x in confirmed])
    []

Let's add an item and confirm it:

    >>> some_object = object()
    >>> secret = box.put(some_object)
    >>> some_data = box.data.get(secret)
    >>> some_data.confirmed = True
    >>> confirmed = box.get_all_confirmed()
    >>> sorted([x for x in confirmed])
    [<object object at ...>]
