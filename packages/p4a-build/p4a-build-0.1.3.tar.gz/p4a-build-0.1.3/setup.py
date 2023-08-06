from distutils.core import setup

setup(
    name='p4a-build',
    version='0.1.3',
    author='Mathieu Virbel',
    author_email='mat@kivy.org',
    scripts=['p4a-build'],
    description='Build tool for P4A Build Cloud',
    install_requires=['requests']
)
