from distutils.core import setup

setup(
    name='MyGithubv2',
    version='0.1.0',
    author='Karthik Sampath',
    author_email='karbrv@gmail.com',
    packages=['myGithub', 'myGithub.test'],
    url='http://pypi.python.org/pypi/MyGithubv2/',
    license='LICENSE.txt',
    description='Useful Github API for v2.',
    long_description=open('README.txt').read(),
)
