Model Setup
============

Dependencies
____________

Python
-------------------------------------------------------------------------------

chitwanabm has been tested to be functional on Linux, Windows 7, and 
Mac OS 10.6.4. The model needs a Python 2.7 installation along with several 
other dependencies:

- Numpy: Numpy is required.

- GDAL/OGR (optional): GDAL is required to read in the GeoTIFF world file and 
  DEM GeoTIFF. OGR is required to output shapefiles of neighborhoods locations 
  and land use.

R and R packages:
-------------------------------------------------------------------------------

Several R scripts are used to initialize the model, to 
generate synthetic populations to be used for running the model 
(if the ICPSR restricted data from the CVFS survey is unavailable), 
and for automated plotting of model results. If you do not have R 
installed, you will need to set the parameter "make_plots" to 
"False" in your chitwanabmrc file.

R (verison 2.15.1 is tested and working) is needed to produce result plots at 
the end of each model run, and to initialize the model from the CVFS survey 
data. The following R packages are used in model initialization and results 
plotting: foreign, ggplot2, reshape, gstat, rgdal, epicalc.

Git (optional)
-------------------------------------------------------------------------------

Git (or msysGit on Windows) is required for the model to be able to save the 
current code version in the chitwanabmrc file that is output together with 
model results at the end of each model run.

Initial Setup
_____________

To get the model, download the latest stable version of the code from 
http://rohan.sdsu.edu/~zvoleff/research/chitwanabm.php.

The development snapshot (the latest version of the code, but it may not always 
be working correctly) can be downloaded from: 
https://github.com/azvoleff/chitwanabm/zipball/master.

The development source can also be downloaded via git from 
git://github.com/azvoleff/chitwanabm.git.

To install the model, simply unzip the code into a folder on your 
computer.  After installing Python and the dependencies listed above, you 
will need to add the folder containing the model to your computer's Python 
path so that the code modules will load correctly.

Setup on Windows
----------------

Setup on Linux and Mac OS
--------------------------

On Linux and Mac OS, you will need to add a line to your user profile telling 
Python where the chitwanabm files are located. You can do this one of two ways.  
To temporarily add the chitwanabm path to your Python path, open XTerm and 
type::

    export PYTHONPATH=/path/to/chitwanabm/folder

Replace "/path/to/chitwanabm/folder" with the correct full path to the 
chitwanabm folder. For example, if the code is on your desktop, this might be 
"/Users/azvoleff/Desktop/chitwanabm" on a Mac, or 
"/home/azvoleff/Desktop/chitwanabm" on Linux.

To make this change permanent, add the line::

    export PYTHONPATH=/path/to/chitwanabm/folder

to the ".profile" file in your home directory.

