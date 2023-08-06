import os
from importlib import import_module
from distutils.core import setup


basedir = os.path.abspath(os.path.dirname(__file__) or '.')


# required data

package_name = 'pylt'
summary = "Python Language Transformations: try alternate syntax"
with open(os.path.join(basedir, 'README')) as readme_file:
     description = readme_file.read()
project_url = "https://bitbucket.org/ericsnowcurrently/pylt/"

# dymanically generated data

version = ".".join(str(val)
                   for val in import_module(package_name).__version__)

# set up packages

modules = []

exclude_dirs = [
        ]

packages = []
for path, dirs, files in os.walk(package_name):
    if "__init__.py" not in files:
        continue
    path = path.split(os.sep)
    if path[-1] in exclude_dirs:
        continue
    packages.append(".".join(path))


# other data

classifiers = [
        #"Development Status :: 1 - Planning",
        #"Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        #"License :: OSI Approved :: Apache Software License",
        #"License :: OSI Approved :: BSD License",
        #"License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        ]


if __name__ == "__main__":
    setup (
            name=package_name,
            version=version,
            author="Eric Snow",
            author_email="ericsnowcurrently@gmail.com",
            url=project_url,
            license="New BSD License",
            description=summary,
            long_description=description,
            classifiers=classifiers,
            packages=packages,
            )
