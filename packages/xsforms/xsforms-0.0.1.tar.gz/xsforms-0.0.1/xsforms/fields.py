from django.forms import fields
from widgets import DateInput

class Field:
    def render_js(self):
        return self.widget.render_js()

class CharField(fields.CharField):
    template = "fields/char-field.html"

    def __init__(self, template, *args, **kwargs):
        fields.CharField.__init__(self, *args, **kwargs)
        self.template = template


class DateField(fields.DateField, Field):
    def __init__(self, input_formats=None, *args, **kwargs):

        widget = DateInput()
        self.widget = widget

        if kwargs.has_key("change_month"):
            widget.change_month = kwargs.pop("change_month")

        if kwargs.has_key("change_year"):
            widget.change_year = kwargs.pop("change_year")

        if kwargs.has_key("min_date"):
            widget.min_date = kwargs.pop("min_date")

        if kwargs.has_key("max_date"):
            widget.max_date = kwargs.pop("max_date")

        fields.DateField.__init__(self, input_formats, *args, **kwargs)
