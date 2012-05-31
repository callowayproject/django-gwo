===================
Management Commands
===================

.. _pull_from_gwo:

pull_from_gwo
=============

Updates the data with the data from Google Website Optimizer.

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

.. _templates_with_variations:

templates_with_variations
=========================

Given a template name, it will drill down through all included templates and return all the templates that have Django-GWO tags within them.

This command only needs the template name::

	$ ./manage.py templates_with_variations blog/post_detail.html
	
	Templates with variation tags:
	------------------------------
	blog/post_detail.html
	blog/top_nav.html
	blog/top_nav.html

This command is handy to use before using ``generate_variation``\ , so you know all the templates that require processing for variations.

.. _generate_variation:

generate_variation
==================

Prints to the console a template with sections replaced with the variation specified in the combination. This makes it easier to recreate the template(s) after the experiment is finished.

This management command needs the template name and the combination number::

	$ ./manage.py generate_variation blog/post_detail.html 5

and you can put the output to a file by::

	$ ./manage.py generate_variation blog/post_detail.html 5 > post_detail.html

``generate_variation`` then requests the combination from Google Website Optimizer. The combination specifies which variation to use with each section. For example, if you had a section in your template specified as:

.. code-block:: django

	{% set_experiment "Example Experiment" %}
	{{ gwo_experiment.control_script|safe }}
	  <h2>{{ object.title }}</h2>
	  {% gwo_start_section "Top Nav" %}<p class="other_posts">{% gwo_end_section "Top Nav" %}

depending on the combination specified, the results could look like:

.. code-block:: django

	
	
	  <h2>{{ object.title }}</h2>
	  <p class="other_posts" style="display: None">

The ``{% set_experiment %}`` tag and ``{{ gwo_experiment }}`` variables are gone, the ``{% gwo_start_section %}`` and ``{% gwo_stop_section %}`` tags are gone, and the contents between them is the value of the variation.

.. note:: 
   **Included templates are not touched.**
   
   If your experiment included markup on templates that were included with the ``{% include %}`` tag, this command does not look at them.

.. note:: 
   **track_click tags are not removed.**
   
   The track_click scripts will work fine without an experiment running. It also saves on adding them back in if a follow-up experiment is run.
