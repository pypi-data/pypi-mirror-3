
.. index:: installation
.. _installation:

Installation
============
These installation instructions are specifically for an Ubuntu Linux system but should work with minor 
changes on other Linux systems and with some changes on other operating systems (Windows, MacOS, etc..). 
For other Linux systems you will need to replace any invocations of ``apt-get`` with your system's package
manager. For other operating systems you will need to work out the corresponding method of install.
The instructions install packages using ``apt-get`` where possible, otherwise they are installed in ``$HOME/local/``.
There are also some `Darwin/MacOS specific installation instructions`_.




.. index:: prerequisites

Prerequisites
-------------
The following software should be downloaded and unpacked/installed somewhere on your system:

- GCC_: I have tested STEME with g++ versions 4.5.1 and 4.6.3 but other recent versions should work. I have had
  reports that gcc 4.2.1 works on a Mac but that gcc 4.0.1 does not. Every release of
  g++ seems to give it a stricter interpretation of the C++ standard so
  perhaps it is not a good idea to try a version too much newer. Other modern 
  compilers such as Microsoft C++ should work but I have not tried them. Please let me know
  if you try other compilers and run into any issues. 
  
  On Ubuntu Linux gcc can be installed using the command::
    
    sudo apt-get install gcc
  
- `Python 2.7`_: Other versions of python 2 will probably work such as 2.5 or 2.6.
  STEME requires the following Python packages:
  
  * numpy
  * matplotlib
  * Bio
  * corebio
  * weblogolib
  * cookbook
  
  In my experience pip_ is the easiest way to install Python packages.
  
  On Ubuntu Linux the above packages can be installed using the commands::
    
    sudo apt-get install python-dev python-numpy python-matplotlib python-biopython python-pip
    sudo pip install corebio
    sudo pip install weblogo
    sudo pip install cookbook
    
- `Boost C++ libraries`_: I have tested STEME using version 1.47, 1.48 and 1.49 of boost, 
  although any recent version should work. If you do not already have the libraries installed,
  first download them. On Ubuntu Linux you can do::
  
    mkdir -p $HOME/local/src
    cd $HOME/local/src
    wget \
      http://sourceforge.net/projects/boost/files/boost/1.49.0/boost_1_49_0.tar.bz2/download \
      -O boost_1_49_0.tar.bz2
    tar jxf boost_1_49_0.tar.bz2
     
  To install boost following the commands_ given at the Boost website is
  straightforward, for example::
  
    cd $HOME/local/src/boost_1_49_0
    ./bootstrap.sh --help
    ./bootstrap.sh --prefix=$HOME/local --with-libraries=python
    ./b2 install release
  
  should install the boost Python library and the necessary headers. Once they are installed,
  you will need to update your ``LD_LIBRARY_PATH`` environment variable, e.g.::
  
    export LD_LIBRARY_PATH=$HOME/local/lib:$LD_LIBRARY_PATH
  
  so that the shared objects can be found at runtime.
        
.. _commands: http://www.boost.org/doc/libs/1_49_0/more/getting_started/unix-variants.html#easy-build-and-install


- `SeqAn sequence analysis library`_: The SeqAn C++ library provides the suffix array implementation that
  STEME uses. I have used the latest SVN version of SeqAn, although any recent version should work.
  Follow the installation instructions. You might need cmake to install it.

  On Ubuntu Linux you can do::

    cd $HOME/local/src
    sudo apt-get install subversion
    svn co http://svn.mi.fu-berlin.de/seqan/trunk/seqan
    cd seqan
    python util/bin/build_forwards.py core/include/seqan
    python util/bin/build_forwards.py extras/include/seqan


.. _GCC: http://gcc.gnu.org/
.. _Python 2.7: http://www.python.org/
.. _Boost C++ libraries: http://www.boost.org/
.. _SeqAn sequence analysis library: http://www.seqan.de/







.. index:: download

Download STEME
--------------

If you have not already done so, download STEME from PyPi_ and unpack it locally.

On Ubuntu Linux you can do::

    cd $HOME/local/src
    wget http://sysbio.mrc-bsu.cam.ac.uk/johns/STEME/dist/steme.tar.gz
    tar zxf steme.tar.gz
    cd $HOME/local/src/steme

.. _PyPi: http://pypi.python.org/pypi?:action=display&name=STEME





.. index:: build environment

Configure, build, install
-------------------------

In this guide we will install STEME into a `virtual Python environment`_. You will not need
to do this if you have administrator permissions on your machine. 
On Ubuntu Linux virtualenv can be installed using the command::
    
    sudo apt-get install python-virtualenv

.. _virtual Python environment: http://www.virtualenv.org/en/latest/index.html

The virtual Python environment can be created thus::
	
	virtualenv --system-site-packages $HOME/local/steme-virtualenv
	export PATH=$HOME/local/steme-virtualenv/bin:$PATH
    
Now we are ready to configure STEME. STEME uses aksetup for installation, which means that
installation should be easy and quick. Try::
  
    python configure.py --help

to examine the possible options. By the way, if a configuration option says ``several ok``,
then you may specify several values, separated by commas. We need to tell STEME
where the boost and seqan C++ libraries are::

    python configure.py \
      --seqan-dir=$HOME/local/src/seqan/ \
      --boost-inc-dir=$HOME/local/include \
      --boost-lib-dir=$HOME/local/lib

Configuration is obtained from files in this order::

    /etc/aksetup-defaults.py
    $HOME/.aksetup-defaults.py
    $PACKAGEDIR/siteconf.py

Once you've run configure, you can copy options from your ``siteconf.py`` file to
one of these files, and you won't ever have to configure them again manually.
In fact, you may pass the options ``--update-user`` and ``--update-global`` to
configure, and it will automatically update these files for you. This is particularly 
handy if you want to perform an unattended or automatic installation via easy_install_.

.. _easy_install: http://packages.python.org/distribute/easy_install.html
.. _pip: http://pypi.python.org/pypi/pip


To check that STEME has been successfully installed
try running the following command::

    steme --help

You should see a list of STEME's runtime options. 





.. index:: Darwin/MacOS specific installation

Darwin/MacOS specific installation instructions
-----------------------------------------------

It should be straightforward to adapt the above instructions for Ubuntu to other Linux systems. However here
is another method of installing STEME that works on a MacOS system. The instructions suppose you are going to install
everything under the ``$HOME/local`` directory and that you have a working copy of python and gcc already installed.
These instructions have been tested with Darwin gcc version 4.2.1 and Darwin Kernel Version 10.7.0.
Unlike the above Ubuntu instructions they do not require root access to install packages. 
First of all create a virtual Python environment to install STEME into::

  mkdir $HOME/local
  cd $HOME/local
  curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
  python virtualenv.py $HOME/local/steme-virtualenv


Install the necessary Python packages::

    $HOME/local/steme-virtualenv/bin/pip install numpy 
    $HOME/local/steme-virtualenv/bin/pip install matplotlib 
    $HOME/local/steme-virtualenv/bin/pip install biopython
    $HOME/local/steme-virtualenv/bin/pip install corebio
    $HOME/local/steme-virtualenv/bin/pip install weblogo
    $HOME/local/steme-virtualenv/bin/pip install cookbook
  
If you see any errors such as::

    IndentationError: unindent does not match any outer indentation level
  
You may need to edit the file mentioned and remove any blank lines at the end.

If you see `errors <http://superuser.com/questions/242190/how-to-install-matplotlib-on-os-x>`_
related to freetype font header files when installing matplotlib,
you might be able to work around them with::

    # see: http://superuser.com/questions/242190/how-to-install-matplotlib-on-os-x
    export LDFLAGS="-L/usr/X11/lib"
    export CFLAGS="-I/usr/X11/include -I/usr/X11/include/freetype2 -I/usr/X11/include/libpng12"


Install the Boost Python indexing suite and the `Boost C++ libraries`_.
Here I have used version 1.48.0 but any recent version should work::

    mkdir $HOME/local/src
    cd $HOME/local/src
    curl -O http://sysbio.mrc-bsu.cam.ac.uk/johns/STEME/dist/indexing_suite_v2.tar.gz
    tar zxf indexing_suite_v2.tar.gz
    curl -o boost_1_48_0.tar.bz2 -L http://downloads.sourceforge.net/project/boost/boost/1.48.0/boost_1_48_0.tar.bz2
    tar jxf boost_1_48_0.tar.bz2
    cd boost_1_48_0/
    ./bootstrap.sh --prefix=$HOME/local --with-libraries=python


Install the `SeqAn sequence analysis library <http://www.seqan.de/>`_. The SeqAn C++ library 
provides the suffix array implementation that
STEME uses. I have used the latest SVN version of SeqAn, although any recent version should work.
You might need to install cmake and subversion for this to work::

  cd $HOME/local/src
  svn co http://svn.mi.fu-berlin.de/seqan/trunk/seqan
  cd seqan
  python util/bin/build_forwards.py core/include/seqan
  python util/bin/build_forwards.py extras/include/seqan


Download STEME and two libraries it depends on and unpack them locally::

  cd $HOME/local/src
  curl -O http://sysbio.mrc-bsu.cam.ac.uk/johns/STEME/dist/steme.tar.gz
  tar zxf steme.tar.gz


If STEME has been built and installed correctly::

  $HOME/local/steme-virtualenv/bin/python -c "import stempy"
  
should execute without errors. If not, you may need to change your ``PYTHONPATH`` environment
variable to point to the STEME python code.

Note that in the instructions on using STEME you will have to replace ``python`` with 
``$HOME/local/steme-virtualenv/bin/python`` as you have installed STEME into a virtual
environment.


 