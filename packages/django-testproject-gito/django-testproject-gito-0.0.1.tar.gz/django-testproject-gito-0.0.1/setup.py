from distutils.core import setup

setup(
    name="django-testproject-gito",
    version="0.0.1",
    author="Vishwas Sharma",
    author_email="vishwas.iitd@gmail.com",
    packages=['django-testproject', 'django-testproject.tests'],
    url='http://vishwassharma.com/packages/django-testproject.tar.gz',
    license='LICENSE.txt',
    description="Django project for making life easy",
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >=1.2",
        # Some other projects also
    ],
)
