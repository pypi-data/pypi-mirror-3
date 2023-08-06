#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright John Reid 2010, 2011, 2012
#

"""
distutils setup script for STEME. Adapted from http://git.tiker.net/pyublas.git/tree.
"""

import os

def read(*fnames):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), *fnames)).read()



def get_config_schema():
    from aksetup_helper import ConfigSchema, Option, \
            IncludeDir, LibraryDir, Libraries, BoostLibraries, \
            Switch, StringListOption, make_boost_base_options

    import sys
    if 'darwin' in sys.platform:
        default_libs = []
        default_cxxflags = ['-arch', 'i386', '-arch', 'x86_64',
                '-isysroot', '/Developer/SDKs/MacOSX10.6.sdk']
        default_ldflags = default_cxxflags[:]
    else:
        default_cxxflags = []
        default_ldflags = []

    return ConfigSchema(
        make_boost_base_options() + [
            BoostLibraries("python"),
            Option("SEQAN_DIR"),
            StringListOption("CXXFLAGS", [], help="Any extra C++ compiler options to include"),
            StringListOption("LDFLAGS", [], help="Any extra linker options to include"),
        ]
    )



def main():
    from aksetup_helper import hack_distutils, get_config, setup, NumpyExtension, find_packages

    hack_distutils()
    conf = get_config(get_config_schema())

    INCLUDE_DIRS = [
        'c++',
        'c++/include',
        'c++/myrrh',
        'c++/hmm',
        'c++/indexing_suite_v2',
        'c++/FAST',
        os.path.join(conf['SEQAN_DIR'], 'core', 'include'),
        os.path.join(conf['SEQAN_DIR'], 'extras', 'include'),
    ] + conf['BOOST_INC_DIR'] 
    LIBRARY_DIRS = conf['BOOST_LIB_DIR']
    LIBRARIES = conf['BOOST_PYTHON_LIBNAME']
    EXTRA_DEFINES = { }

    try:
        from distutils.command.build_py import build_py_2to3 as build_py
    except ImportError:
        # 2.x
        from distutils.command.build_py import build_py
        
    #
    # C++ extension
    #
    cStempy = NumpyExtension(
        'stempy._release_build._stempy',
        [
            'c++/myrrh/src/python/multi_array_to_numpy.cpp',
            'c++/FAST/HS.cpp',
            'c++/FAST/motif_evaluator.cpp',
            'c++/FAST/theta_fns.cpp',
            'c++/FAST/minimize.cpp',
            'c++/FAST/convolution.cpp',
            'c++/FAST/fft.cpp',
            'c++/FAST/utils.cpp',
            'c++/FAST/llr_score.cpp',
            'c++/python/python_utility.cpp',
            'c++/python/python_seqan.cpp',
            'c++/python/python_markov.cpp',
            'c++/python/python_data.cpp',
            'c++/python/python_bg.cpp',
            'c++/python/python_bs.cpp',
            'c++/python/python_model.cpp',
            'c++/python/python_llr_pvalues.cpp',
            'c++/python/python_significance.cpp',
            'c++/python/python_descender.cpp',
            'c++/python/python_find_instances.cpp',
            'c++/python/python_find_best_w_mers.cpp',
            'c++/python/python_start_finder.cpp',
            'c++/python/python_em.cpp',
            'c++/python/python_module.cpp',
            'c++/pvalues/parse.cpp',
            'c++/pvalues/bejerano.cpp',
            'c++/pvalues/fast.cpp',
            'c++/pvalues/shifted_hirji.cpp',
            'c++/pvalues/pval.cpp',
            'c++/pvalues/pvalue_test_defs.cpp',
        ],
        include_dirs         = INCLUDE_DIRS,
        library_dirs         = LIBRARY_DIRS,
        libraries            = LIBRARIES,
        define_macros        = list(EXTRA_DEFINES.items()),
        extra_compile_args   = conf['CXXFLAGS'] + [
                                    "-Wno-unused",
                                    "-Wno-deprecated",
                                    "-finline-functions",
                                    "-ftemplate-depth-128",
                                    "-DSEQAN_ENABLE_TESTING=0", 
                                    "-DSEQAN_ENABLE_DEBUG=0",
                                    "-DBOOST_DISABLE_ASSERTS",
                                    "-DMYRRH_DISABLE_ASSERTS",
                                    "-DPVAL_LOOKUP",
                                    "-DNDEBUG",
                                ],
        extra_link_args      = conf['LDFLAGS'] + [
                                    '-lrt',
                                    '-lfftw3',
                                ],
    )
    
    setup(
        name                 = 'STEME',
        version              = read('python', 'stempy', 'VERSION').strip().split('-')[0],
        description          = 'STEME: an accurate efficient motif finder for large data sets.',
        long_description     = read('python', 'stempy', 'README'),
        author               ='John Reid',
        author_email         ='johnbaronreid@netscape.net',
        license              = 'BSD',
        url                  ='http://sysbio.mrc-bsu.cam.ac.uk/johns/STEME/',
        classifiers          = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
            'Programming Language :: C++',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Utilities',
        ],

        packages             = find_packages(where='python'),
        package_dir          = { '' : 'python' },
        #py_modules           = ['pybool.examples.tutorial'],
        package_data         = { 'stempy': ['README', 'LICENSE', 'VERSION'] },
        install_requires     = ['distribute', 'cookbook'],
        scripts              = [
                                'python/scripts/steme',
                                'python/scripts/steme-em',
                               ],
        ext_modules          = [cStempy],

        # 2to3 invocation
        cmdclass             = {'build_py': build_py},
        
        include_package_data = False,
    )





if __name__ == '__main__':
    main()

