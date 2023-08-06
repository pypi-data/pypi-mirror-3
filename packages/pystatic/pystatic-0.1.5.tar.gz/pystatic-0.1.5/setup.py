from distutils.core import setup
setup(
    name = "pystatic",
    packages = ["pystatic"],
    scripts=["pystatic/scripts/pystatic"],
    package_data={"pystatic": ["templates/*"]},
    version = "0.1.5",
    description = "Static Website Generator",
    author = "Vasco Pinho",
    author_email = "vascogpinho@gmail.com",
    url = "https://github.com/vascop/pystatic",
    download_url = "https://github.com/vascop/pystatic/zipball/master",
    keywords = ["generator", "static website", "html"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Code Generators",
        ],
    long_description = """\
Static Website Generator
------------------------

Generates static websites using Django's Templating Engine
You can make use of variables, template inheritance and filters
which greatly speed up development and facilitate maintenance.
Has a simple server for local development

"""
)
