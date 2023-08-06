from distutils.core import setup


setup(
    name = "django-historylinks",
    version = "1.0.0",
    description = "Automatic SEO-friendly HTTP 301 redirects if the URL of a model changes.",
    long_description = open("README.md").read(),
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "http://github.com/etianen/django-historylinks",
    download_url = "http://github.com/downloads/etianen/django-historylinks/django-historylinks-1.0.0.tar.gz",
    zip_safe = False,
    packages = [
        "historylinks",
        "historylinks.management",
        "historylinks.management.commands",
        "historylinks.migrations",
    ],
    package_dir = {
        "": "src",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)