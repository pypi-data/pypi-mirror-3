from setuptools import setup, find_packages

setup(
    name='django-mimemail',
    version='0.1',
    packages=find_packages(),
    install_requires=['django', 'beautifulsoup'],
    author="Mads Sulau Joergensen",
    author_email="mads@sulau.dk",
    description='Helper library for sending mime-mails with inline pictures.',
    license='BSD',
    url='http://bitbucket.org/madssj/django-mimemail/'
)

