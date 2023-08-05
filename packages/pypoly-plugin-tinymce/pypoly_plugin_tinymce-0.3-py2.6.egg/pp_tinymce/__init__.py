import pypoly
from pypoly.component import Component
from pypoly.content.webpage import JavaScript
from pypoly.content.webpage.form.text import WYSIWYG

__version__ = "0.3"


class Main(Component):
    def start(self):
        pypoly.hook.register(
            "content.web.webpage.head",
            "tinymce",
            tinymce_hook
        )
        return True


def tinymce_hook(webpage=None, *args, **kwargs):
    editor_ids = []
    for child in webpage.get_childs(level=None):
        if isinstance(child, WYSIWYG) == True:
            editor_ids.append(child.id)

    if len(editor_ids) == 0:
        # don't load the javascript if no editor exists on the webpage
        return []

    source = """
        tinyMCE.init({
            mode : "exact",
            elements : "%(editor_ids)s",
            theme : "advanced",
            theme_advanced_toolbar_location : "top",
            theme_advanced_toolbar_align : "left",
            theme_advanced_statusbar_location : "bottom",
            theme_advanced_resizing : true,
            theme_advanced_resize_horizontal : false,
            width : "100%%",
        });
    """ % {
        "editor_ids": ",".join(editor_ids)
    }

    return [
        JavaScript(
            url=pypoly.url(
                "/plugin/tinymce/tiny_mce/tiny_mce.js",
                plain=True
            )
        ),
        JavaScript(source=source)
    ]
