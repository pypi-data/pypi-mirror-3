from Products.Archetypes import atapi

class EmailWidget(atapi.StringWidget):
    """Class for presenting emails as accessible."""

    _properties = atapi.StringWidget._properties.copy()

    _properties.update({
            'macro':"EmailWidget"
            })
