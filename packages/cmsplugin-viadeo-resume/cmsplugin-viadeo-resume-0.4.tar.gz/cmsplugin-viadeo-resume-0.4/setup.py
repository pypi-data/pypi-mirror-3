from setuptools import setup
import os

setup(
    name = "cmsplugin-viadeo-resume",
    packages = ['cmsplugin_viadeo_resume',],

    package_data = {
        '': [
            'templates/cmsplugin_viadeo_resume/*.html',
            'locale/*/LC_MESSAGES/*.po'
        ]
    },

    version = "0.4",
    description = "Viadeo resume plugin for django-cms 2.2",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author = "Antoine Nguyen",
    author_email = "tonio@ngyn.org",
    url = "http://bitbucket.org/tonioo/cmsplugin-viadeo-resume",
    license = "BSD",
    keywords = ["django", "django-cms", "viadeo", "resume"],
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
    install_requires = ['Django-CMS>=2.2', 'oauth2', 'simplejson'],
    )
