# Makefile for building jccjmx
#
# based on Makefile for PyLucene 

VERSION=0.1

# 
# You need to uncomment and edit the variables below in the section
# corresponding to your operating system.
#
# Windows drive-absolute paths need to be expressed cygwin style.
#
# PREFIX: where programs are normally installed on your system (Unix).
# PREFIX_PYTHON: where your version of python is installed.
# JCC: how jcc is invoked, depending on the python version:
#  - python 2.7:
#      $(PYTHON) -m jcc
#  - python 2.6:
#      $(PYTHON) -m jcc.__main__
#  - python 2.5:
#      $(PYTHON) -m jcc
#  - python 2.4:
#      $(PYTHON) $(PREFIX_PYTHON)/lib/python2.4/site-packages/jcc/__main__.py
# generates all C++ classes into one single file. This may exceed a compiler
# limit.
#

# Mac OS X 10.6 (64-bit Python 2.6, Java 1.6)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc.__main__ --shared --arch x86_64

# Mac OS X 10.6 (MacPorts 1.8.0 64-bit Python 2.7, Java 1.6)
#PREFIX_PYTHON=/opt/local
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc --shared --arch x86_64

# Mac OS X 10.6 (MacPorts 1.8.0 64-bit Python 2.6, Java 1.6)
#PREFIX_PYTHON=/opt/local
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc.__main__ --shared --arch x86_64

# Mac OS X 10.6 (64-bit and 32-bit Python 2.6 together, Java 1.6)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc.__main__ --shared --arch x86_64 --arch i386

# Mac OS X 10.5 (32-bit Python 2.5, Java 1.5)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc --shared

# Mac OS X  (Python 2.3.5, Java 1.5, setuptools 0.6c7, Intel Mac OS X 10.4)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) /System/Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/JCC-2.3-py2.3-macosx-10.4-i386.egg/jcc/__init__.py

# Mac OS X  (Python 2.3.5, Java 1.5, setuptools 0.6c7, PPC Mac OS X 10.4)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) /System/Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/JCC-2.3-py2.3-macosx-10.4-ppc.egg/jcc/__init__.py

# Linux     (Ubuntu 6.06, Python 2.4, Java 1.5, no setuptools)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) $(PREFIX_PYTHON)/lib/python2.4/site-packages/jcc/__init__.py

# Linux     (Ubuntu 8.10 64-bit, Python 2.5.2, OpenJDK 1.6, setuptools 0.6c9)
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc --shared

# FreeBSD
#PREFIX_PYTHON=/usr
#ANT=ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) -m jcc

# Solaris   (Solaris 11, Python 2.4 32-bit, Sun Studio 12, Java 1.6)
#PREFIX_PYTHON=/usr
#ANT=/usr/local/apache-ant-1.7.0/bin/ant
#PYTHON=$(PREFIX_PYTHON)/bin/python
#JCC=$(PYTHON) $(PREFIX_PYTHON)/lib/python2.4/site-packages/jcc/__init__.py

# Windows   (Win32, Python 2.5.1, Java 1.6, ant 1.7.0)
#PREFIX_PYTHON=/cygdrive/o/Python-2.5.2/PCbuild
#ANT=JAVA_HOME=o:\\Java\\jdk1.6.0_02 /cygdrive/o/java/apache-ant-1.7.0/bin/ant
#PYTHON=$(PREFIX_PYTHON)/python.exe
#JCC=$(PYTHON) -m jcc --shared

# Windows   (Win32, msys/MinGW, Python 2.6.4, Java 1.6, ant 1.7.1 (WinAnt))
#PREFIX_PYTHON=/c/Python26
#ANT=JAVA_HOME="c:\\Program Files\\Java\\jdk1.6.0_18" "/c/Program Files/WinAnt/bin/ant"
#PYTHON=$(PREFIX_PYTHON)/python.exe
#JCC=$(PYTHON) -m jcc.__main__ --shared --compiler mingw32

# Windows   (Win32, Python 2.7, Java 1.6, ant 1.8.1, Java not on PATH)
#PREFIX_PYTHON=/cygdrive/c/Python27
#ANT=JAVA_HOME=c:\\jdk1.6.0_22 /cygdrive/c/java/apache-ant-1.8.1/bin/ant
#PYTHON=$(PREFIX_PYTHON)/python.exe
#JCC=$(PYTHON) -m jcc --shared --find-jvm-dll

ANT=ant
PYTHON=python2.7
JCC=$(PYTHON) -m jcc.__main__ --shared

ifeq ($(DEBUG),1)
  DEBUG_OPT=--debug
endif

JCCJMX_JAR=jccjmx.jar
JARS=$(JCCJMX_JAR)

DEFINES=-DJCCJMX_VER="\"$(VERSION)\""

.PHONY: generate compile install default all clean realclean \
	test jars distrib

default: all

$(JCCJMX_JAR):
	$(ANT)

JCCFLAGS?=

jars: $(JARS)

GENERATE=$(JCC) $(foreach jar,$(JARS),--jar $(jar)) \
           $(JCCFLAGS) \
           --python jccjmx \
           --import lucene \
           --version $(VERSION) \
           --files 1

generate: jars
	$(GENERATE)

compile: jars
	$(GENERATE) --build $(DEBUG_OPT)

install: jars
	$(GENERATE) --install $(DEBUG_OPT) $(INSTALL_OPT)

bdist: jars
	$(GENERATE) --bdist

wininst: jars
	$(GENERATE) --wininst

all: jars compile

clean:
	$(ANT) clean

realclean: clean
	rm -rf build dist

test:
	$(PYTHON) -m doctest README.txt

distrib:
	$(PYTHON) setup.py sdist

