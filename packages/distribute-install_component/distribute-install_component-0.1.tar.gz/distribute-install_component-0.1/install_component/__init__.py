from distutils.errors import DistutilsArgError
from setuptools import Command


class InstallComponent(Command):
    user_options = [
        ('list', 'l', "List components available to install"),
    ]
    description = "Install optional components listed in extras_require"
    command_consumes_arguments = True

    def initialize_options(self):
        self.args = None
        self.list = False

    def finalize_options(self):
        """We don't take any options so far."""
        if not self.list and not self.args:
            raise DistutilsArgError("No components specified, use -l to list.")

        self.extras = self.distribution.extras_require or {}

    def run(self):
        if self.list:
            if self.extras:
                print '\n'.join(self.extras.keys())
            else:
                print "No optional components."
        else:
            easy_install = self.distribution.get_command_class('easy_install')
            for component in self.args:
                try:
                    deps = self.extras[component]
                except KeyError:
                    raise DistutilsArgError("No such component %s" % component)

                e = easy_install(
                    self.distribution, args=deps
                )
                e.finalize_options()
                e.run()

