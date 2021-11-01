# django-formset – Better UX for Django Forms 

`<django-formset>` is a [Webcomponent](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
to wrap one or more Django Forms. This webcomponent is installed together with the Django app
**django-formset**.


## Installation

Install **django-formset** using

```shell
pip install django-formset
```

change `settings.py` to

```python
INSTALLED_APPS = [
    ...
    'formset',
    ...
]
```


## Usage

Say, we have a standard Django Form:

```python
from django.forms import forms, fields

class SubscribeForm(forms.Form):
    last_name = fields.CharField(
        label="Last name",
        min_length=2,
        max_length=50,
    )

    # ... more fields
```

when rendering to HTML, we can wrap that Form into our special Webcomponent:

```html
{% load static formsetify %}
<html>
  <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script type="module" src="{% static 'formset/js/django-formset.min.js' %}"></script>
  </head>
  <body>
    <!-- other stuff -->
    <django-formset endpoint="{{ request.path }}">
      {% render_form form "bootstrap" field_classes="mb-2" %}
      <button type="button" click="disable -> submit -> proceed !~ scrollToError" class="btn">Submit</button>
    </django-formset>
    <!-- other stuff -->
  </body>
</html>
```

in our `urls.py` we now wire everything together:

```python
from django.urls import path
from formset.views import FormView

from .myforms import SubscribeForm


urlpatterns = [
    ...
    path('subscribe', FormView.as_view(
        form_class=SubscribeForm,
        template_name='testapp/extended-form.html',
        success_url='/success',
    )),
    ...
]
```

This renders our Subscribe Form with a much better User Experience. We get immediate feedback if
input entered into a field is not valid. Moreover, when this form is submitted but rejected by the
server-side validation, errors are shown immediatly and without reloading the page. Only on success,
a new new page is loaded.


## Motivation

Instead of using a `<form>`-tag and include all its fields, here we wrap the complete form
inside the special Webcomponent `<django-formset>`. This allows us to communicate via Ajax with
our Django view, using the named endpoint. This means, that we can wrap multiple `<form>`-elements
into our Formset. It also means, that we now can place the Submit `<button>`-element outside of the
`<form>`-element. By doing so, we can decouple the Form's business-logic from its technical
constraint, of transferring a group of fields from and to the server. 

When designing this library, the main goal was to keep the programming interface a near as possible
to the way Django handles Forms, Models and Views.


## Some Highlights

* Before submitting, our Form is prevalidated by the browser, using the constraints we defined for
  each Django Field.
* The Form's data is send by an Ajax request, preventing a full page reload. This gives a much
  better user experience.
* Server side validation errors are sent back to the browser, and rendered near the offending
  Form Field.
* Non-field validation errors are renderer together with the form.
* CSRF-tokens are handlet trough a Cookie, hence there is no need to add that token to each form.
* Forms can be rendered for different CSS frameworks using their specific styleguides for arranging
  HTML. Currently **django-formset** includes renderers for
  [Bootstrap](https://getbootstrap.com/docs/5.0/forms/overview/),
  [Bulma](https://bulma.io/documentation/form/general/),
  [Foundation](https://get.foundation/sites/docs/forms.html),
  [Tailwind](https://tailwindcss.com/) [^1] and [UIKit](https://getuikit.com/docs/form).
* Support for all standard widgets Django currently offers. This also includes radio buttons and
  multiple checkboxes with options.
* File uploads are handled asynchrounosly. This means that the user opens the file dialog or drags a
  file to the form. This file then is uploaded immediatly to a temporary folder, returning a unique
  handle together with a thumbnail of it. On form submission, this handle then is used to access
  that file and proceed as usual.
* Select boxes with too many entries, can be filtered by the server using a search query. No extra
  endpoint is required for this feature.
* Radio buttons and multiple checkboxes with only a few fields can be rendered inlined rather than
  beneath each other.
* The Submit buttons can be configured as a chain of actions. It for instance is possible to change
  the CSS depending on success or failure, add delays and specify the further proceedings. This
  for instance allows to specify the success page in HTML rather than in the Django View.
* A Formset can group multiple Forms into a collection. On submission, this collection then is
  sent to the server as a group a separate entities. After all Forms have been validated, the
  submitted data is provided as a nested Python dictionary.
* Such a Form-Collection can be declared to have many Form entities of the same kind. This allows to
  create siblings of Forms, similar the Django's Admin Inline Forms. However, each of these siblings
  can contain other Form-Collections, which themselves can also be declared as siblings. This list
  of siblings can be extended or reduced using one "Add" and multiple "Remove" buttons.
* By using the special attributes `show-if="condition"`, `hide-if="condition"` or
  `disable-if="condition"` on input fields or fieldsets, one can hide or disable these marked
  fields. This `condition` can evaluate all field values of the current Formset by a Boolean
  expression.
* The client part, has no dependencies to any JavaScript-framework. It is written in pure TypeScript
  and compiles to a single, portable JS-file.

[^1]: Tailwind is special here, since it doesn't include purpose-built form control classes out of
      the box. Instead **django-formset** offers an opinionated set of CSS classes suitable for
      Tailwind.


## Documentation

Not deployed on RTD, but some documentation can be found in the `docs` folder.


## Motivation

This library shall replace the Form-validation framework in django-angular.


[![Build Status](https://github.com/jrief/django-formset/actions/workflows/pythonpackage.yml/badge.svg)]()
[![PyPI version](https://img.shields.io/pypi/v/django-formset.svg)](https://pypi.python.org/pypi/django-formset)
[![Django versions](https://img.shields.io/pypi/djversions/django-formset)](https://pypi.python.org/pypi/django-formset)
[![Python versions](https://img.shields.io/pypi/pyversions/django-formset.svg)](https://pypi.python.org/pypi/django-formset)
[![Software license](https://img.shields.io/pypi/l/django-formset.svg)](https://github.com/jrief/django-formset/blob/master/LICENSE)
