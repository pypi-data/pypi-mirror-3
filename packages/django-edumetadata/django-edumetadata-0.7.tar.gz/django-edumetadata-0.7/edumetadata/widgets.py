from django import forms


class SortFieldWidgetWrapper(forms.Widget):
    """
    This class is a wrapper to a given widget to add the add up/down arrows
    for the admin interface.
    """

    def _media(self):
        return self.widget.media
    media = property(_media)

    def render(self, name, value, *args, **kwargs):
        output = [self.widget.render(name, value, *args, **kwargs)]
        output.append(u'<a class="up" href="#">up</a>&nbsp;')
        output.append(u'<a class="dn" href="#">dn</a>')
