# PMAT-PDK
Photonics design kit (PDK) written in Python and used to standardize photonic components, route (and autoroute!) waveguides, all for generation of lithography masks. Library was built ontop of gdsCAD for Python. Written by Derek Kita at MIT for use in the photonic materials research group (PMAT).

First install, then check out the tutorial at: https://github.com/DerekK88/pmat_pdk/wiki/PMAT-PDK-Homepage

Derek Kita, 2016

---------------------------------------------------------------------------------------------------------------------

Installing software for PMAT-PDK:

(1) Install python 2.7 from:
	https://www.continuum.io/downloads
	
* Make sure numpy and matplotlib are installed by running
	
	`$ import numpy`
	or
	`$ import matplotlib`

(2) Install the shapely library from:
	http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
	
* If you are using a 64-bit system, make sure you install:
	`Shapely-1.5.16-cp27-cp27m-win_amd64.whl`
* Open a command prompt (type "CMD" into the windows search tab) and navigate to the Downloads folder, then enter:
	
	`$ pip install Shapely-1.5.16-cp27-cp27m-win_amd64.whl`

(3) Install the descartes library from:
	https://pypi.python.org/pypi/descartes

* You will want to download the file:
	descartes-1.0.2-py2-none-any.whl

* Using the same command prompt, enter:
	
	`$ pip install descartes-1.0.2-py2-none-any.whl`

(4) Install the dxfgrabber library from:
	https://pypi.python.org/pypi/dxfgrabber

* There is only a python 3.5 version available, so this will need to be installed from source.
* Download and unzip the file:
	`dxfgrabber-0.8.0.zip`
* In the command prompt, navigate to the file that contains setup.py, then enter:
	
	`$ python setup.py install`

(5) Finally, install gdsCAD from:
	https://pypi.python.org/pypi/gdsCAD

* Unpack the tarball (.tar.gz file) and navigate to the file with setup.py in your command window, then run:
	
	`$ python setup.py install`

(6) Now close any python IDE and reopen.  You may have to restart your computer if the pythonpath doesn't find these libraries.  Test by entering:

	$ import descartes
	$ import shapely
	$ import dxfgrabber

(7) Now, everything should work find, except there's one bug in the core code for gdsCAD, so now we have to do some surgery:
* Navigate to the core.py file.  For me, this was found in the following path:

	`C:\Users\dkita\Anaconda2\lib\site-packages\gdscad-0.4.5-py2.7.egg\gdsCAD\core.py`

* Open the file in Spyder, and go to line 105.  It should have the following code:
	
	`colors += matplotlib.cm.gist_ncar(np.linspace(0.98, 0, 15))`

* Change this line to read:

	`colors += list(matplotlib.cm.gist_ncar(np.linspace(0.98, 0, 15)))`

* And now you should be good to go for visualizing your structures in matplotlib

(8) Once all these work, you are ready to use the gdsCAD library.  For information on the gdsCAD library, please refer to:

	http://pythonhosted.org/gdsCAD/#

(9) To use PMAT-PDK, first download the "pmat_pdk" file, and locate your Python Path.  To do this, type:

	import sys
	print sys.path
	
in a python terminal.  Choose the path that contains all of your other python packages.  For me, this was:

	`C:\\Users\\dkita\\Anaconda2\\Lib\\site-packages`
	
* Now you can go ahead and place the "pmat_pdk" file here.  Close and relaunch your IDE to reload the Python Path, and then test to see if the package is installed by running (in a python terminal):

	`import pmat_pdk`
	
* To use the "pmat_pdk" library, simply include the following two lines at the beginning of each mask file:

	`from pmat_pdk import *`
	
	`import pmat_pdk.toolkit as tk`

That's it, enjoy! :)

Check out https://github.com/DerekK88/pmat_pdk/wiki/PMAT-PDK-Homepage to see a step-by-step tutorial for making your first lithography mask in Python.
