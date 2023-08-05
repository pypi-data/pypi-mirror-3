from distutils.core import setup

setup(
    name = 'txLibravatar',
    version = '1.0',
    description = 'Twisted module for Libravatar',
    author = 'Francois Marier',
    author_email = 'francois@libravatar.org',
    url = 'https://launchpad.net/txlibravatar',
    py_modules = ['txlibravatar'],
    license = 'MIT',
    keywords = ['libravatar', 'avatars', 'autonomous', 'social', 'federated', 'twisted'],
    requires = ['pylibravatar'],
    classifiers = [
        "Framework :: Twisted",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
txLibravatar is an easy way to make use of the federated `Libravatar`_
avatar hosting service from within your Twisted applications.

See the `project page`_ to file bugs or ask questions.

.. _Libravatar: https://www.libravatar.org/
.. _project page: https://launchpad.net/txlibravatar
"""
    )
