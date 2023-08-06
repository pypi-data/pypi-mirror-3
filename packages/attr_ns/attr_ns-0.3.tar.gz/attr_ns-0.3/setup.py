from distutils.core import setup


PROJECT_SITE = "https://bitbucket.org/ericsnowcurrently"

setup(
        name='attr_ns',
        version="0.3",
        description="A collection of tools relating to namespaces.",
        author="Eric Snow",
        author_email="ericsnowcurrently@gmail.com",
        url="{}/odds_and_ends/src/default/ns".format(PROJECT_SITE),
        packages=['attr_ns', 'attr_ns.tests'],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        )
