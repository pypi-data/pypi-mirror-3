from distutils.core import setup
import biometrics

setup(
    name = "django-biometrics",
    version = biometrics.__version__,
    description = "Associate biometric markers with users",
    url = "http://bitbucket.org/schinckel/django-biometrics/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "biometrics",
        "biometrics.models",
        "biometrics.migrations"
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
