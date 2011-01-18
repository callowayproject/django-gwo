=====================================
Multivariate testing of dynamic pages
=====================================

Why multivariate instead of A/B?
********************************

A/B tests two or more entirely different pages. Google Website Optimizer does this by redirecting the user to different URLs. In many web frameworks, where the URLs are dynamically routed, this is just not practical.

Why is testing dynamic pages so hard?
*************************************

Typically multivariate testing relies on two static URLs: a static URL for testing and a static URL for the conversion.

Dynamic websites -- websites with constantly changing content like blogs and news sites -- can't use this procedure because one URL isn't *really* representative of the site. Every page which uses the underlying template is.

Even static URLs won't work if you have dynamic content on them. For example, if your home page has the most recent blog entries, you can't test what makes more people go to any entry.

Working around the problem
==========================

With Google Website Optimizer, there are ways to work around the typical testing workflow. It is trickier in that you still can't test truly dynamic data, but you can test the static stuff *around* the dynamic data. First you have to understand how GWO tracks users, :term:`combination`\ s and :term:`conversion`\ s.

How GWO performs a test
***********************

#. The :term:`control script` requests the dynamic file ``siteopt.js``\ .

#. ``siteopt.js`` checks cookies for a previously viewed combination or sets cookies to a specific combination and defines the ``utmx_section`` function for later use.

#. ``utmx_section`` function calls potentially replace the original HTML markup with either the previously viewed version, or a newly chosen version.

#. The :term:`tracking script` executes and registers the combination to GWO.

#. The :term:`conversion script` executes when a conversion occurs (traditionally on the conversion page).

See also: `The Techie Guide to Google Website Optimizer <http://static.googleusercontent.com/external_content/untrusted_dlcp/www.google.com/en/us/websiteoptimizer/techieguide.pdf>`_


Spoofing the conversion
***********************

Since GWO uses a JavaScript function to signal a conversion, we are going to use the ``onclick`` methods on ``<a>`` tags to quickly register the conversion before sending the user on their way.

Glossary
========

.. glossary::
	:sorted:

	Experiment
		The test.
	
	Section
		Parts of the template which will vary. Google Website Optimizer uses JavaScript to insert the content into these areas, so make sure the parts that you are testing will allow JavaScript to fill it.
	
	Variation
		A bit of content for a section of an experiment. Google Website Optimizer fills this content into the section with JavaScript.
	
	Combination
		A unique arrangement of one variation for each section.

	Conversion
		A successful test.

	Control Script
		The JavaScript code at the beginning of the page that requests ``siteopt.js`` and sets up the experiment.
	
	Tracking Script
		The JavaScript code at the end of the page that submits the combination shown to the user back to GWO.

	Conversion Script
		The JavaScript code that registers a successful conversion and the combination to GWO.