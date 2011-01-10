
Getting Started
===============

Multivariate testing of dynamic pages

Content of the page is dynamic, but the template is constant
Conversion page is dynamic, but link is constant

Creating an experiment
======================

Create a `multivariate experiment <https://www.google.com/analytics/siteopt/planning>`_ with Google Website Optimizer first. 

#. For step one, select a page (url) that is formatted using the template. For example, if you are testing a blog entry page, pick a recent blog entry for the page url.

#. For step two, decide what parts of the page you are going to test

#. For step three, since you are probably the technical team, it isn't really necessary.

#. For step four, you don't have to worry about. We will be tracking the conversion using javascript.

#. Click on the checkbox at the bottom of the page labeled "I've completed the steps above and I'm ready to start setting up my experiment." and then the create button.

Step One
********

#. Name your experiment.

#. Put in the URL of the representative page for the **Test page URL**

#. Put in the same URL for the **Conversion page URL**

#. Click the continue button


Step Two
********

#. Select **You will install and validate the JavaScript tags**

#. Click the continue button

#. Now, **in a new window,** create a new GWO Experiment in the Django admin.

#. Give the Django GWO experiment the same name you entered in Website Optimizer (for sanity reasons)

#. Copy the control script from the Website Optimizer page and paste it into the control script field in the GWO experiment record.

#. Copy the tracking script from the Website Optimizer page and paste it into the tracking script field in the GWO experiment record.

#. Copy the conversion script from the Website Optimizer page and paste it into the conversion script field in the GWO experiment record.

Step Two-A: Tagging the template
********************************

Before you can go on with Website Optimizer, you need to tag the pages so google can validate them. Django-GWO provides some easy tags to make the process easier than the instructions in Website Optimizer.

#. At the top of the template, add ``{% load gwo_tags %}``\ .

#. In the ``<head>`` section of the page add ``{% gwo_control_script ExperimentName %}``\ . This inserts the copied control script for ``ExperimentName`` into the page.

#. Just before the ``</body>`` tag of the template add ``{% gwo_tracking_script %}``

#. Around each section that you are testing add::

	{% gwo_section SectionName %}
	
	... your original content ...
	
	{% end_gwo_section %}

   The ``SectionName`` is passed through directly to the Website Optimizer JavaScript for the section name.

