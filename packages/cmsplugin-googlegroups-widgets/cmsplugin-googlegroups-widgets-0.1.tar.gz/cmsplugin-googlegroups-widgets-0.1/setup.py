from setuptools import setup, find_packages
import os

setup(
    name = "cmsplugin-googlegroups-widgets",
    packages = find_packages(),

    package_data = {
        'cmsplugin_googlegroups_widgets': [
            'templates/cmsplugin_googlegroups_widgets/*.html',
        ]
    },

    version = "0.1",
    description = "Google Groups widgets for django-cms 2.2",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author = "Antoine Nguyen",
    author_email = "tonio@ngyn.org",
    url = "http://bitbucket.org/tonioo/cmsplugin-googlegroups-widgets",
    license = "BSD",
    keywords = ["django", "django-cms", "google groups", "widgets"],
    classifiers = [
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django"
        ],
    include_package_data = True,
    zip_safe = False,
    install_requires = ['Django-CMS>=2.2'],
    )
