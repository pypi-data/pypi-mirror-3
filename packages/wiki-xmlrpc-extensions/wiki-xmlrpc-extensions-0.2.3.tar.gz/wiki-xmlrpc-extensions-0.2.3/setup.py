# The README.txt file should be written in reST so that PyPI can use
# it to generate your project's PyPI page. 
long_description = open('README.txt').read()

from setuptools import setup, find_packages

setup(
    name="wiki-xmlrpc-extensions",
    version="0.2.3",
    description="wiki xmlrpc tools for interacting with a MoinMoin Wiki",
    long_description=long_description,
    classifiers="Development Status :: 5 - Production/Stable",
    keywords="MoinMoin, xmlrpc",
    maintainer="Reimar Bauer",
    maintainer_email="rb.proj@googlemail.com",
    author="Reimar Bauer",
    author_email="rb.proj@googlemail.com",
    license="Gnu GPL",
    url="https://utils.icg.kfa-juelich.de/docs/wiki-xmlrpc-extensions/",
    platforms="any",
    packages=find_packages(),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=["argparse", ],
    entry_points=dict(
        console_scripts=[
                         'ForkWikiContent = Wiki_XMLRPC_Extensions.ForkWikiContent:main',
                         'ListPages = Wiki_XMLRPC_Extensions.ListPages:main',
                         'ReceiveFiles = Wiki_XMLRPC_Extensions.ReceiveFiles:main',
                         'SendFiles = Wiki_XMLRPC_Extensions.SendFiles:main',
                         ],
    ),
)

