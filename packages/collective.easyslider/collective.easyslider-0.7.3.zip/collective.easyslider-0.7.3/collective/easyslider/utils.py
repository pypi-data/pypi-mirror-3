
def slider_settings_css(settings):
    """
    defined here because then it can be used in the widget
    and view that use the same .pt
    """
    return """
    div.slide li {
        width: %(width)ipx;
        height: %(height)ipx;
    }
    """ % {
        'width' : settings.width,
        'height' : settings.height
    }

    