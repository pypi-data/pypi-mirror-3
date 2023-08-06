from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name = "okonomi",
    version = "0.1.1",
    packages = find_packages(),
    author = "Cox Media Group",
    author_email = "opensource@coxinc.com",
    description = "smart JS loading for Django",
    license = "MIT",
    url = "https://github.com/coxmediagroup/okonomi",
    zip_safe = False,
    keywords = "javascript, loader, templatetag, django",
    long_description = long_description,
    classifiers = [
                    'Development Status :: 4 - Beta',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: MIT License',
                    'Topic :: Software Development :: Build Tools',
                    'Topic :: Software Development :: Libraries',
                    'Topic :: Software Development :: Testing',
                    'Topic :: Utilities',
                    'Operating System :: MacOS :: MacOS X',
                    'Operating System :: Microsoft :: Windows',
                    'Operating System :: POSIX',
                    'Programming Language :: Python :: 2.5',
                    'Programming Language :: Python :: 2.6',
                    'Programming Language :: Python :: 2.7',
                  ]
)
