#!/bin/sh
#
# $Author: cnobile $
# $Date: 2011-12-31 17:05:18 $
# $Revision: 1.4 $
#
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
(cd src; ./dll_test)
exit 0
