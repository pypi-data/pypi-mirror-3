from distutils.core import setup


PROJECT_SITE = "https://bitbucket.org/ericsnowcurrently"


setup(
        name='mogrify',
        version="0.1",
        description="Expand parameter marker formatting, a la PEP 249.",
        author="Eric Snow",
        author_email="ericsnowcurrently@gmail.com",
        url="{}/odds_and_ends/src/default/mogrify".format(PROJECT_SITE),
        py_modules=['mogrify'],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        )
