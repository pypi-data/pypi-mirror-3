"""PasteScript templates"""

from paste.script.templates import Template
from paste.script.templates import var


class MerlotBuildoutTemplate(Template):
    """A PasteScript template for a basic Merlot buildout"""

    egg_plugins = ['Merlot']
    summary = 'A basic Merlot buildout'
    required_templates = []
    _template_dir = 'merlot_buildout'
    use_cheetah = True

    vars = [
        var('merlot_version', 'Merlot version', default='0.2',),
        ]
