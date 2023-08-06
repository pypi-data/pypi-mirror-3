from templer.core.basic_namespace import BasicNamespace


class ToothBasicNamespace(BasicNamespace):
    _template_dir = 'templates/tooth_nested_namespace'
    summary = "A custom basic Python project"
    help = """
This creates a Tooth Python project.
"""
    required_templates = []
    use_cheetah = True
