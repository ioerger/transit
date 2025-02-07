#!/usr/bin/env python

# Copyright 2015.
#   Michael A. DeJesus, Chaitra Ambadipudi, and  Thomas R. Ioerger.
#
#
#    This file is part of TRANSIT.
#
#    TRANSIT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License.
#
#
#    TRANSIT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TRANSIT.  If not, see <http://www.gnu.org/licenses/>.
import sys
import pytpp.__main__
import pytransit.__main__

if __name__ == "__main__":
  print("=== Transit %s ===" % pytransit.__version__)
  print("""
******************************************************************************************
*** Attention: 
***   The 'tnseq-transit' package on PyPi is migrating to a new package name, 'transit1'.  
***   This name-change was required by PyPi. 
***   This is the final release for 'tnseq-transit'.  
***   For subsequent updates, users should do 'pip install transit1'. 
******************************************************************************************
""")
  pytpp.__main__.run_main()

