#!/usr/bin/env python

try:
    import distribute_setup
    distribute_setup.use_setuptools()
except ImportError:
    # For documentation we load setup.py to get version
    # so it does not matter if importing fails
    pass

import os, sys

from setuptools import setup, find_packages

# Has to be last import as it seems something is changing it somewhere
from distutils.extension import Extension

NAME = 'Orange-Text'
DOCUMENTATION_NAME = 'Orange Text Mining'

VERSION = '1.2a1'

DESCRIPTION = 'Orange Text Mining add-on for Orange data mining software package.'
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
AUTHOR = 'Bioinformatics Laboratory, FRI UL'
AUTHOR_EMAIL = 'contact@orange.biolab.si'
URL = 'http://orange.biolab.si/addons/'
DOWNLOAD_URL = 'https://bitbucket.org/biolab/orange-text/downloads'
LICENSE = 'GPLv3'

KEYWORDS = (
    'data mining',
    'machine learning',
    'artificial intelligence',
    'text mining',
    'orange',
    'orange add-on',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
)

PACKAGES = find_packages(
    exclude = ('*.tests', '*.tests.*', 'tests.*', 'tests'),
)

PACKAGE_DATA = {
}

SETUP_REQUIRES = (
    'setuptools',
)

INSTALL_REQUIRES = (
    'Orange',
    'setuptools',
),

EXTRAS_REQUIRE = {
    'GUI': (
        # Dependencies which are problematic to install automatically
        #'PyQt', # No setup.py
    ),
}

DEPENDENCY_LINKS = (
)

ENTRY_POINTS = {
    'orange.addons': (
        'text = _text',
    ),
    'orange.widgets': (
        'Text Mining = _text.widgets',
        # This should be unneeded, because module given should load (register)
        # all wanted widgets and prototypes should just have a flag, but for now ...
        'Prototypes = _text.widgets.prototypes',
    ),
    'orange.data.io.search_paths': (
        'text = _text:datasets',
    ),
}

extra_compile_args = [
    '-fno-strict-aliasing',
    '-Wall',
    '-Wno-sign-compare',
    '-Woverloaded-virtual',
]

extra_link_args = [
]

if sys.platform == 'win32':
    # For MinGW compiler
    extra_link_args += [
        '-static-libgcc',
        '-static-libstdc++',
    ]
    
EXT_MODULES = [
    Extension(
        '_text._orngTextWrapper',
        sources = [
            'src/orngTextWrapper/Wrapper_wrap.cxx',
            'src/orngTextWrapper/Wrapper.cpp',
            'src/tmt/common/Common.cpp',
            'src/tmt/common/Files.cpp',
            'src/tmt/lemmatization/FSADictionary.cpp',
            'src/tmt/lemmatization/FSALemmatization.cpp',
            'src/tmt/lemmatization/Lemmatization.cpp',
            'src/tmt/lemmatization/PorterStemmer.cpp',
            'src/tmt/strings/StringUtils.cpp',
            'src/tmt/strings/UTF8Tokenizer.cpp',
            'src/lemmagen/RdrLemmatizer.cpp',
        ],
        language = 'c++',
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
        include_dirs = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')),
        ],
        define_macros = [
            ('TMTNOZLIB', '1'),
            ('NDEBUG', '1'),
        ],
    ),
]

if __name__ == '__main__':
    setup(
        name = NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        download_url = DOWNLOAD_URL,
        license = LICENSE,
        keywords = KEYWORDS,
        classifiers = CLASSIFIERS,
        packages = PACKAGES,
        package_data = PACKAGE_DATA,
        setup_requires = SETUP_REQUIRES,
        install_requires = INSTALL_REQUIRES,
        extras_require = EXTRAS_REQUIRE,
        dependency_links = DEPENDENCY_LINKS,
        entry_points = ENTRY_POINTS,
        include_package_data = True,
        zip_safe = False,
        ext_modules = EXT_MODULES,
    )
