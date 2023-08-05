import pkg_resources

import pypoly

__version__ = "0.3"

def run():
    path = pkg_resources.resource_filename(
        "tuvedi.admin",
        "templates"
    )

    pypoly.config.set_pypoly("template.path", path)
    pypoly.config.set_pypoly("template.default", "tuvedi")
    pypoly.config.set_pypoly("template.templates", ["tuvedi"])

    pypoly.run()
