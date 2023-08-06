from setuptools import setup, find_packages

version = "0.1.2"

setup(
    name = "exml",
    version = version,
    description = "Easy (for me) XML builder",
    url = "http://bitbucket.org/dpwiz/exml/",
    author = "Alexander Bondarenko",
    author_email = "wiz@aenor.ru",

    packages = find_packages(),
    include_package_data = True,

    license = "MIT",
    keywords = "xml builder",
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
