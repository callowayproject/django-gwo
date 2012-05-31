========
Tutorial
========

We want to get people to go to other blog posts. In our example blog app, the blog entries have next and previous post links at the top of the page and only at the top of the page. Does moving the links to the bottom of the blog entry increase the amount of times people click on them?

To test this question we are going to run a multivariate experiment with two sections ("Top Nav" and "Bottom Nav"). Each variation will have two variations: the "Original" and an alternate. The "Top Nav" Original variation will show the navigation and the alternate will not show the navigation. The "Bottom Nav" Original variation will not show the navigation and the alternate will show the navigation.

GWO will test all four possible combinations: 

======== ============ ============
Name     Top Nav      Bottom Nav
======== ============ ============
Original showing      not showing
Combo 2  showing      showing
Combo 3  not showing  showing
Combo 4  not showing  showing
======== ============ ============


Starting out
============

Make sure that you have a ``local_settings.py`` file with settings for ``GWO_USER``\ , ``GWO_PASSWORD``\ , ``GWO_ACCOUNT``\ .



1. Create example experiment (link to those docs)
2. If you go to the Google Website Optimizer site, you'll see the experiment.
3. Click on the Add Section link
4. Name the section "Top Nav"
5. Click on "Save and add another"
6. Name the section "Bottom Nav"
7. Click on "Save"

Original template state
=======================

GWO wants at least one "Original" variation and one additional variation for each section. Each variation contains the raw content that GWO will dynamically insert into the document. **As a result, the section and variation can not contain anything dynamic on the page.** This means that we are going to have to play some tricks to test what we want to test.

We are going to alter the template to include the blog post navigation, but use inline CSS to hide them. We will define the sections around the ``<p>`` tag.

First, let's get the template to its "original" state.

.. highlight:: django

1. Open the ``blog/templates/blog/post_detail.html`` template, and copy the lines 12 - 19 (these lines here)::

	<p class="other_posts">
	  {% if object.get_previous_by_publish %}
	  <a class="previous" href="{{ object.get_previous_by_publish.get_absolute_url }}" title="{% trans "View previous post" %}">&laquo; {{ object.get_previous_by_publish }}</a>
	  {% endif %}
	  {% if object.get_next_by_publish %}
	  | <a class="next" href="{{ object.get_next_by_publish.get_absolute_url }}" title="{% trans "View next post" %}">{{ object.get_next_by_publish }} &raquo;</a>
	  {% endif %}
	</p>

2. Paste it just after (around lines 27 - 29)::

	<div class="body">
	  {{ object.body|safe }}
	</div>

   If you were to render a blog entry right now, the next and previous post links would appear above and below the entry. 

3. To make the bottom links disappear, we'll add some inline CSS to the bottom ``<p>`` tag::

	<p class="other_posts" style="display: None">

   Now rendering a blog entry shows the links at the top, but not at the bottom. We have our "original" state::

	<div class="body">
	  {{ object.body|safe }}
	</div>
	<p class="other_posts" style="display:None">
	  {% if object.get_previous_by_publish %}
	  <a class="previous" href="{{ object.get_previous_by_publish.get_absolute_url }}" title="{% trans "View previous post" %}">&laquo; {{ object.get_previous_by_publish }}</a>
	  {% endif %}
	  {% if object.get_next_by_publish %}
	  | <a class="next" href="{{ object.get_next_by_publish.get_absolute_url }}" title="{% trans "View next post" %}">{{ object.get_next_by_publish }} &raquo;</a>
	  {% endif %}
	</p>


Add in the template tags
========================

#. In line 3, change the ``{% load i18n comments %}`` to::

	{% load i18n comments gwo_tags %}

#. We need to specify the experiment we are using. The ``{% set_experiment %}`` template tag does this for us. Due to the Django template language, the ``{% set_experiment %}`` value is only seen within its current ``{% block %}``. For the sake of this tutorial, we'll put everything within ``{% block content %}``\ .
   
   On line 11, right after ``{% block content_title %}``\ , insert::
	{% set_experiment "Example Experiment" %}
	{{ gwo_experiment.control_script|safe }}

   
   On line 26, right after ``{% block content %}``\ , insert::

	{% set_experiment "Example Experiment" %}

#. Just before the last ``{% endblock %}``\ (around line 68), add::

	{{ gwo_experiment.tracking_script|safe }}

   to include another script that GWO needs.

Define the sections in the template
===================================

To define the sections, we will use the template tags ``{% gwo_start section %}`` and ``{% gwo_end_section %}``\ .

#. Around line 14, change ``<p class="other_posts">`` to::

	{% gwo_start_section "Top Nav" %}<p class="other_posts">{% gwo_end_section "Top Nav" %}

#. Around line 33, change ``<p class="other_posts" style="display: None">`` to::

	{% gwo_start_section "Bottom Nav" %}<p class="other_posts" style="display: None">{% gwo_end_section "Bottom Nav" %}


Create Top Nav Original Variation
=================================

**Title:** ``Original``

**Content:** ``<p class="other_posts">``

Create Top Nav Alternate Variation
==================================

**Title:** ``Not Showing``

**Content:** ``<p class="other_posts" style="display: None">``

Create Bottom Nav Original Variation
====================================

**Title:** ``Original``

**Content:** ``<p class="other_posts" style="display: None">``

Create Bottom Nav Alternate Variation
=====================================

**Title:** ``Showing``

**Content:** ``<p class="other_posts">``


Instrumenting the links
=======================

Adding the script
*****************

To let Google Website Optimizer know that a conversion has occurred we need to  use a script. At the bottom of the template, just before the ``{% endblock %}``\ , around line 70, add:: 

	{% trackclick_script %}

The ``trackclick_script`` template tag renders the template ``gwo/trackclick_script.html``\ , which a snippet of JavaScript that looks like::

	<script type="text/javascript" charset="utf-8">
	function trackclick(that){
	try {
		{{ conversion_script|safe }}
		setTimeout('document.location = "' + that.href + '"', 100);
	}catch(err){}
	}</script>

The ``trackclick()`` function will change the location of the browser to the URL passed to it. The function also allows us to do a few things before it changes. The ``{{ conversion_script|safe }}`` variable is set to the appropriate pieces of the conversion script passed back to us from Google.

The ``trackclick()`` function is designed to work regardless of whether there is currently an active experiment.

Modifying the tags
******************

We need to call the ``trackclick`` script from each ``<a>`` tag that counts as a successful conversion. The template tag ``{% trackclick %}`` renders ``gwo/trackclick.html`` which looks like::

	onclick="trackclick(this);return false;"

By rendering a template, it allows you to add additional commands or functions easily.

We need to modify the two sets of ``<a>`` tags by adding ``{% trackclick %}`` within the tag. The first one is around line 16 and also around line 35::

	<a class="previous" href="{{ object.get_previous_by_publish.get_absolute_url }}" {% trackclick %} title="{% trans "View previous post" %}">&laquo; {{ object.get_previous_by_publish }}</a>

The next set is around line 19 and also around line 38::

	| <a class="next" href="{{ object.get_next_by_publish.get_absolute_url }}" {% trackclick %} title="{% trans "View next post" %}">{{ object.get_next_by_publish }} &raquo;</a>

Starting the experiment
=======================

Once everything is set up, you can start the experiment.

#. Make sure all your template changes are deployed on your site

#. In the admin, go to the GWO Experiment change list

#. Click on ``Start`` in the Status field of this experiment

Finishing the experiment
========================

After a period of time, Google Website Optimizer will inform you of their winning combination(s). You can stop the experiment.

#. Click on ``Stop`` next to the experiment's ``Running`` status in the Django admin.


Updating the templates
======================

Which templates did I modify?
*****************************

Once the experiment has run its course and you have the winning combination, you need to implement that combination within the templates and strip out all the Django-GWO template tags. To make it even more fun, there could be more than one template if you have several included templates.

Management commands to the rescue!

To discover the templates that have tags and thus require changing, run the :ref:`templates_with_variations` command. The output will look something like this::

	$ ./management.py templates_with_variations blog/post_detail.html
	
	Templates with variation tags:
	------------------------------
	blog/post_detail.html

The example project has a template with includes called ``post_detail.final.inc.html`` which outputs::

	$ ./management.py templates_with_variations blog/post_detail.final.inc.html

	Templates with variation tags:
	------------------------------
	blog/post_detail.html
	blog/top_nav.html
	blog/top_nav.html

Making the substitution
***********************

You now need to run each template returned from :ref:`templates_with_variations` command through :ref:`generate_variation`\ . This command takes a template name and a combination number (the winning combination from Google Website Optimizer) and prints the template with Django-GWO tags stripped and proper variation substituted to the screen.

Why to the screen? Two reasons. Django-GWO doesn't take for granted that you want to change the original file, and it is incredibly easy to redirect the output to a file of your choosing.

The command::

	$ ./manage.py generate_variation blog/post_detail.html 5 > post_detail.html

will create a file called ``post_detail.html`` in the project folder with the substitutions. You can test it, modify it, or simply replace the old template with it.