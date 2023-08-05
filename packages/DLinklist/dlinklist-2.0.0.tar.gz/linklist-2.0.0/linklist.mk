#
# $Author: cnobile $
# $Date: 2012-01-11 03:16:40 $
# $Revision: 1.2 $
#

# Change the directory paths below to reflect your system.
PREFIX	= /usr/local
LIBDIR	= $(PREFIX)/lib
INCDIR	= $(PREFIX)/include
DOCLIB	= $(PREFIX)/share/doc

# Version and date info (DO NOT MODIFY)
MAJORVERSION	= 2
MINORVERSION	= 0
PATCHLEVEL	= 0
VERSION		= ${MAJORVERSION}.${MINORVERSION}.${PATCHLEVEL}
TODAY		= $(shell date +"%Y-%m-%d_%H%M")
