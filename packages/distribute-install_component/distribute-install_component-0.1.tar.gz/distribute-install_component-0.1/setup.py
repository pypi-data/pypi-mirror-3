from setuptools import setup

desc = 'Distribute extension to install components listed in extras_require'
setup(
    name='distribute-install_component',
    version='0.1',
    description=desc,
    long_description=open('README').read(),
    packages=['install_component'],
    author='Daniel Pope',
    author_email='mauve@mauveweb.co.uk',
    url='https://bitbucket.org/lordmauve/distribute-install_component',
    entry_points={
        "distutils.commands": [
            "install_component = install_component:InstallComponent",
        ],
    },
)
