from distutils.core import setup
setup(
    name = "djchart",
    packages = ["djchart", "djchart.templatetags"],
    version = "0.1.2",
    description = "Charts for Django",
    author = "Artyom Shein",
    author_email = "sc-djchart@aisys.ru",
    url = "https://github.com/temiy/djchart",
    download_url = "https://github.com/temiy/djchart",
    keywords = ["charts"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Graphics :: Charts",
        ],
    long_description = """\
Django chart
-------------------------------------

JS charts for Django.
"""
)
