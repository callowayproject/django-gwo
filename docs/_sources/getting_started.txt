===============
Getting Started
===============


Creating an experiment
======================

#. Create a new Experiment in the Django admin.

#. Name your experiment in the **Title** field.

#. Set 'Multivariate' as the **Experiment type**.

#. Put in the URL of the representative page for the **Test page URL**. For example, if you are testing a blog entry page, pick a recent blog entry for the page url.

#. Put in the same URL for the **Conversion page URL**

#. Leave **Auto prune mode** at None, unless you really know what you're doing.

#. Save the experiment.


Create a section for an experiment
==================================

#. Each listing of experiments includes a field detailing how many sections are currently defined for that experiment and links to view the experiment's sections or add a section. Click on **Add section**.

#. The **Experiment** field will already be set, so simply enter in the **Title** for this section.

#. Clicking on **Save** will save this section and take you to the list of all sections. Clicking on **Save and add another** will save this section and allow you to add a new section.


Create a variation for an experiment
====================================

#. Each list of sections includes a field detailing how many variations are currently defined for that section and links to view the section's variations or add a variation to the section. Click on **Add variation**.

#. The **Experiment**


Tagging the template
====================

Before you can go on with Website Optimizer, you need to tag the pages so google can validate them. Django-GWO provides some easy tags to make the process easier than the instructions in Website Optimizer.

#. At the top of the template, add ``{% load gwo_tags %}``\ .

#. In the ``<head>`` section of the page add ``{% gwo_control_script ExperimentName %}``\ . This inserts the copied control script for ``ExperimentName`` into the page.

#. Just before the ``</body>`` tag of the template add ``{% gwo_tracking_script %}``

#. Around each section that you are testing add::

	{% gwo_section SectionName %}
	
	... your original content ...
	
	{% end_gwo_section %}

   The ``SectionName`` is passed through directly to the Website Optimizer JavaScript for the section name.

