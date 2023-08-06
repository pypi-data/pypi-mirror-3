from templer.core.basic_namespace import BasicNamespace
from templer.core.vars import StringVar
from templer.core.vars import EASY
from templer.core.vars import EXPERT

class InvisibleStringVar(StringVar):

    def __repr__(self):
        return self.default


class ToothBasicNamespace(BasicNamespace):
    _template_dir = 'templates/tooth_nested_namespace'
    summary = "A custom basic Python project"
    help = """
This creates a Tooth Python project.
"""
    required_templates = []
    use_cheetah = True

    def check_vars(self, vars, cmd):
        vars = super(BasicNamespace, self).check_vars(vars, cmd)
        vars['travisci'] =  InvisibleStringVar(
            'travisci',
            title='Travis-CI',
            description='Travis-Ci',
            default='.travis.ci',
            modes=(EASY, EXPERT),
            page='Metadata',
            help="""
Travis-CI
"""
            )

        vars['zopeskel'] =  InvisibleStringVar(
            'zopeskel',
            title='ZopeSkel',
            description='ZopeSkel',
            default='.zopeskel',
            modes=(EASY, EXPERT),
            page='Metadata',
            help="""
ZopeSkel
"""
            )
        return vars
