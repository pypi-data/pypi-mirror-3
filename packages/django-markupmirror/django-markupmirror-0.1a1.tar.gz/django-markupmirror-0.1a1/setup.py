import os

from setuptools import setup
from setuptools import find_packages


AUTHORS = (
    ("Fabian B\xc3\xbcchler", "fabian.buechler@gmail.com"),
)


def read(*parts):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))
    content = ""
    fp = open(path)
    content = fp.read()
    fp.close()
    return content


setup(
    name='django-markupmirror',
    version=__import__('markupmirror').get_version(),
    author=", ".join([a[0] for a in AUTHORS]),
    author_email=", ".join([a[1] for a in AUTHORS]),
    description="Django field and widget for editing markup content.",
    long_description='\n\n'.join([
        read('README.rst'),
        read('docs', 'quickstart.rst'),
        read('docs', 'changelog.rst'),
        ]),
    url="https://bitbucket.org/fabianbuechler/django-markupmirror",
    keywords="django markup field widget codemirror",
    license="BSD License",
    platforms=["OS Independent"],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
)
