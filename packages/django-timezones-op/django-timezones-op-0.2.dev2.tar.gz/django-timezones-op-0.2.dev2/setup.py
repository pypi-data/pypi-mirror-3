from setuptools import setup

setup(
    name = "django-timezones-op",
    version = __import__("timezones").__version__,
    author = "Manuel Francisco, Brian Rosner",
    author_email = "manuel@aircable.net, brosner@gmail.com",
    description = "A Django reusable app to deal with timezone localization for users modified for OP",
    long_description = open("README").read(),
    url = "http://github.com/OpenProximity/django-timezones/",
    license = "BSD",
    packages = [
        "timezones",
        "timezones.templatetags",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Framework :: Django",
    ]
)