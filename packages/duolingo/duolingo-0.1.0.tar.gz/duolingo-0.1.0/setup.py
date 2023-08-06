from distutils.core import setup

setup(
    name='duolingo',
    version='0.1.0',
    author='Severin Hacker',
    author_email='severin@duolingo.com',
    packages=['duolingo'],
    scripts=[],
    url='http://duolingo.com',
    license='LICENSE.txt',
    description='python client for the duolingo API',
    long_description=open('README.txt').read(),
    install_requires=[
        "oauth2 >= 1.5.211",
        "httplib2 >= 0.7.2",
    ],
)