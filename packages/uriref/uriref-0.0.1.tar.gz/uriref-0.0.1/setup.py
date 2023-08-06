from distutils.core import setup
setup(
    name = "uriref",
    packages = ["uriref"],
    version = "0.0.1",
    description = "Regex Based URI reference parsing",
    author = "Berend (mpe)",
    author_email = "berend@dotmpe.com",
    url = "http://project.dotmpe.com/uriref",
#    download_url = "",
    keywords = ["url", "uri"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description = """\
URL and URN parser written in regular expressions. 
Based on RFC 2396 BNF terms, update to RFC 3986 planned but not started.
"""
)
