from django.forms import fields, forms


class AddressForm(forms.Form):
    """
    Address Form
    ------------

    Sometimes it is desirable to align certain input fields inside the same row. For this purpose
    the Bootstrap framework offers special CSS classes. To make use of that, we can add a dictionary
    to our Form class such as

    .. code-block:: python

        class AddressForm(...):
            ...
            css_classes = {
                'form_css_classes': 'row',
                'field_css_classes': {
                    '*': 'mb-2 col-12',
                    'postal_code': 'mb-2 col-4',
                    'city': 'mb-2 col-8',
                },
            }
            ...

    This modifies the rendering of the form by wrapping the named fields ``postal_code`` and ``city``
    into a ``<django-field-group class="...">`` using the named classes. The key value ``'*'`` is used
    as a wildcard matching all other field names.
    """

    recipient = fields.CharField(
        label="Recipient",
        max_length=100,
    )

    postal_code = fields.CharField(
        label="Postal Code",
        max_length=8,
    )

    city = fields.CharField(
        label="City",
        max_length=50,
    )


