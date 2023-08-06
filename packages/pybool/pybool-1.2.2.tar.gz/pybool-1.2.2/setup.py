#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright John Reid 2010, 2011, 2012
#

"""
distutils setup script for pybool. Adapted from http://git.tiker.net/pyublas.git/tree.
"""


def get_config_schema():
    from aksetup_helper import ConfigSchema, Option, \
            IncludeDir, LibraryDir, Libraries, BoostLibraries, \
            Switch, StringListOption, make_boost_base_options

    return ConfigSchema(
        make_boost_base_options() + [
            BoostLibraries("python"),
    
            StringListOption("CXXFLAGS", ["-Wno-sign-compare"], 
                help="Any extra C++ compiler options to include"),
            StringListOption("LDFLAGS", [], 
                help="Any extra linker options to include"),
        ]
    )




def main():
    from aksetup_helper import hack_distutils, get_config, setup, NumpyExtension
    import pybool


    hack_distutils()
    conf = get_config(get_config_schema())

    INCLUDE_DIRS = ["C++/myrrh"] + conf["BOOST_INC_DIR"] 
    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    EXTRA_DEFINES = { }

    ext_src = [
        "C++/module_network.cpp",
        "C++/myrrh/src/python/multi_array_to_numpy.cpp",
    ]

    try:
        from distutils.command.build_py import build_py_2to3 as build_py
    except ImportError:
        # 2.x
        from distutils.command.build_py import build_py
        
    #
    # C++ extension
    #
    cNetwork = NumpyExtension(
        'pybool.cNetwork',
        ext_src,
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        define_macros=list(EXTRA_DEFINES.items()),
        extra_compile_args=conf["CXXFLAGS"],
        extra_link_args=conf["LDFLAGS"],
    )
    
    setup(
        name                 = 'pybool',
        version              = pybool.__release__,
        description          = 'pybool: A package to infer Boolean networks.',
        long_description     = """
            pybool: A python package that infers Boolean networks given a set of constraints.
            
            Consider the common scenario of a biologist who is studying a particular
            regulatory network. They study a set of genes that are known to play a role in the
            network. They have some background knowledge of particular regulatory connections
            from his own studies or from the literature. In addition to this they have
            perturbation data that reveals the temporal order of expression of the genes under
            some conditions. For example, these could be derived from loss-of-function
            or over-expression experiments. The biologist would like to elucidate the entire
            network and to this end can perform various experiments to test particular regulatory
            connections. These experiments are costly and time-consuming. Which
            connections should they focus on? This is where the pybool package can help.
            By modelling candidate regulatory networks using Boolean logic, pybool evaluates
            which networks are consistent with the perturbation data and the known
            regulatory connections.
        """,
        url                  ='http://sysbio.mrc-bsu.cam.ac.uk/johns/pybool/',
        author               ='John Reid',
        author_email         ='john.reid@mrc-bsu.cam.ac.uk',
        license              = "free for academic use",
        
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
            'Programming Language :: Python :: 3',
            'Programming Language :: C++',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Utilities',
        ],

        packages             = ['pybool'],
        py_modules           = ['pybool.examples.tutorial'],
        #py_modules=['pybool.examples.tutorial', 'distribute_setup', 'configure', 'aksetup_helper'],
        scripts              = ['scripts/pybool_run_constraints.py'],
        ext_modules          = [cNetwork],

        # 2to3 invocation
        cmdclass             = {'build_py': build_py},
        
        include_package_data = False,
    )





if __name__ == '__main__':
    main()

