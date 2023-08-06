import re
import sys
import setuptools
from pylint import lint

_opts = lint.Run.LinterClass.make_options()

def user_options():
    parsed = []

    for longopt, params in _opts:
        desc = params.get('help', None)

        parsed.append(('lint-' + longopt + '=', None, desc))
    return parsed

class PylintCommand(setuptools.Command):
    description = "run pylint on all your modules"
    user_options = user_options() + [
        ('lint-exclude-packages=', None, 'exclude these packages'),
        ('lint-output=', None, "output report into this file"),
    ]

    def initialize_options(self):
        self.lint_exclude_packages = 'tests test'
        self.lint_output = None
        for longopt, params in _opts:
            setattr(self, 'lint_' + longopt.replace('-', '_').rstrip('='), None)

    def finalize_options(self):
        self.lint_exclude_packages = [module.strip() \
            for module in re.split('[\s,]+', self.lint_exclude_packages)]
        if self.lint_output:
            self.lint_output = open(self.lint_output, 'w')

    def run(self):
        options = []
        for longopt, params in _opts:
            value = getattr(self, 'lint_' + longopt.replace('-', '_'))
            if value is not None:
                if ' ' in value:
                    value = '"' + value + '"'
                options.append('--{0}={1}'.format(longopt, value))

        files = []
        base = self.get_finalized_command('build_py')
        for (package, module, filename) in base.find_all_modules():
            if package in self.lint_exclude_packages:
                continue
            files.append(filename)

        if self.lint_output:
            stdout, sys.stdout = sys.stdout, self.lint_output
            stderr, sys.stdout = sys.stderr, self.lint_output
        lint.Run(options + files)
        if self.lint_output:
            sys.stdout = stdout
            sys.stderr = stderr
