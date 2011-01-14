===================
Management Commands
===================

pull_from_gwo
=============

Updates the data with the data from Google Website Optimizer. Local versions are deleted and recreated.

::

	$ ./manage.py pull_from_gwo
	Purging local experiments
	Pulling experiments from Google Website Optimizer
	 Building experiment Example Experiment
	  Pulling sections
	  Building section Top Nav
	   Pulling variations
	   Building variation Original
	   Building variation Not Showing
	  Building section Bottom Nav
	   Pulling variations
	   Building variation Original
	   Building variation Showing
	Done.


