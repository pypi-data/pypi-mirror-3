from Products.Archetypes import atapi

class URIWidget(atapi.StringWidget):
    """Class for presenting URIs as accessible."""

    _properties = atapi.StringWidget._properties.copy()

    _properties.update({
            'macro':"URIWidget"
            })
