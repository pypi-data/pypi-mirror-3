from django.forms import fields
from django.template.loader import render_to_string

class Widget:
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = dict(self.attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        print attrs
        if attrs.has_key("id"):
            self.html_id = attrs["id"]
        return attrs

class DateInput(Widget, fields.DateInput):
    max_date = None
    min_date = None
    change_month = None
    change_year = None
    date_format = "dd-mm-yyyy"

    def render_js(self):
        return render_to_string('js/date-field.js', {
            "max_date":self.max_date,
            "min_date": self.min_date,
            "change_year": self.change_year,
            "change_month": self.change_month,
            "id": self.html_id,
            "date_format": self.date_format
        })

