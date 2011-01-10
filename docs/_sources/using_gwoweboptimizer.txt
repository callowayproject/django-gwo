======================================
Using the weboptimizer gdata Extension
======================================

General Experiment Tasks
========================

Get list of experiments
***********************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp_feed = c.get_experiments()

``exp`` is now a :class:`ExperimentFeed` instance. Each :py:class:`ExperimentEntry` is found in the :py:attr:`ExperimentFeed.entry` attribute:

.. code-block:: python

	for exp in exp_feed.entry:
	    print exp.to_string(pretty_print=True)

Each of the experiments in the feed are summary instances only, meaning they don't have detailed information. For more detailed information, you need to request a specific experiment.

Get detailed info about an experiment
*************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.get_experiment(client.ExperimentQuery('12345'))

Alternatively, if you have already queried a list of experiments you can use the ``href`` property of the ``get_self_link()`` method of the entry:

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp_feed = c.get_experiments()
	exp1 = c.get_experiment(exp_feed.entry[0].get_self_link().href)

Or you can create an :py:class:`ExperimentQuery` using the ``text`` property of the ``experiment_id`` property:

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp_feed = c.get_experiments()
	ex1 = exp_feed.entry[0]
	exp1 = c.get_experiment(client.ExperimentQuery(ex1.experiment_id.text))


Update an experiment
********************

Updating an experiment is easy as long as you remember that all the attributes are actually XML tags. Typically you have to update the ``text`` attribute. 

.. note::

	**force=True** is the only way I've been able to get the REST API to actually update the experiment.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp = c.get_experiment(client.ExperimentQuery('12345'))
	exp.title.text = 'Test Exp 1'
	exp = c.update(exp, force=True)

The test URL and goal URL attributes aren't easy to update, so there are two methods to make it easy: :py:meth:`ExperimentEntry.update_test_link` and :py:meth:`ExperimentEntry.update_goal_link`\ .

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp = c.get_experiment(client.ExperimentQuery('12345'))
	exp.update_goal_link('http://www.example.com/new/goal/')
	exp = c.update(exp, force=True)


Delete an experiment
********************

You delete experiments by passing either a URI (:py:class:`ExperimentQuery`\ ) or an :py:class:`ExperimentEntry` instance to the :py:meth:`WebsiteOptimizerClient.delete` method.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	response = c.delete(client.ExperimentQuery('12345'))

The response is a :py:class:`httplib.HTTPResponse` instance. :py:attr:`httplib.HTTPResponse.status` should be 200 if everything was successful.

Copy an experiment
******************

TODO


View all combinations in an experiment
**************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	combo_feed = c.get_combinations(client.CombinationQuery(experiment='12345'))

``combo_feed`` is a :py:class:`CombinationFeed` instance. All combinations are found in the :py:attr:`CombinationFeed.entry` attribute.

View a single combination in an experiment
******************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	combo = c.get_combination(client.CombinationQuery(experiment='12345', '0'))

Launch a follow-up experiment
*****************************

TODO


A/B Experiments
===============

Create a new A/B experiment
***************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp = c.add_experiment(
	    exp_type='AB', 
	    analytics_acct='1234567', 
	    test_url='http://www.example.com/test/url/', 
	    goal_url='http://www.example.com/goal/url/',
	    title='Test Exp 2')

``exp`` is now a :class:`ExperimentEntry` instance as returned from Google. If there is an problem, :py:meth:`WebsiteOptimizerClient.add_experiment` raises a :py:exc:`gdata.client.RequestError` exception.


Add a new page variation to an A/B experiment
*********************************************

View a single page variation in an A/B experiment
*************************************************

View all page variations in an A/B experiment
*********************************************

Update a page variation in an A/B experiment
********************************************

Delete a page variation from an A/B experiment
**********************************************

Multivariate Experiments
========================

Create a new multivariate experiment
************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	exp = c.add_experiment(
	    exp_type='Multivariate', 
	    analytics_acct='1234567', 
	    test_url='http://www.example.com/test/url/', 
	    goal_url='http://www.example.com/goal/url/',
	    title='Test Exp 2')

``exp`` is now a :class:`ExperimentEntry` instance as returned from Google. If there is an problem, :py:meth:`WebsiteOptimizerClient.add_experiment` raises a :py:exc:`gdata.client.RequestError` exception.


View all sections in a multivariate experiment
**********************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.get_experiment(client.ExperimentQuery('12345'))
	sections = c.get_sections(client.SectionQuery(experiment))


``sections`` is a :py:class:`SectionFeed` instance. Individual sections are in the :py:attr:`SectionFeed.entry` attribute.


View a single section in a multivariate experiment
**************************************************

Sections are numbered starting at 0. There will be :py:attr:`ExperimentEntry.num_sections.text` sections within the experiment.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.get_experiment(client.ExperimentQuery('12345'))
	section = c.get_section(client.SectionQuery(experiment, 0))


Add a new section to a multivariate experiment
**********************************************

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.add_experiment(
	    exp_type='Multivariate', 
	    analytics_acct='1234567', 
	    test_url='http://www.example.com/test/url/', 
	    goal_url='http://www.example.com/goal/url/',
	    title='Test Exp 2')
	section = c.add_section(experiment, title='section1')

``section`` is now a :class:`SectionEntry` instance. If there is an problem, :py:meth:`WebsiteOptimizerClient.add_section` raises a :py:exc:`gdata.client.RequestError` exception.


Update a section in a multivariate experiment
*********************************************

Updating a section is easy as long as you remember that all the attributes are actually XML tags. Typically you have to update the ``text`` attribute. 

.. note::

	**force=True** is the only way I've been able to get the REST API to actually update the section.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	section = c.get_section(client.SectionQuery('12345', '0'))
	section.title.text = 'Inner Column'
	section = c.update(section, force=True)


Delete a section from a multivariate experiment
***********************************************

You delete sections by passing either a URI (:py:class:`SectionQuery`\ ) or an :py:class:`SectionEntry` instance to the :py:meth:`WebsiteOptimizerClient.delete` method.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	response = c.delete(client.SectionQuery('12345', '1'))

The response is a :py:class:`httplib.HTTPResponse` instance. :py:attr:`httplib.HTTPResponse.status` should be 200 if everything was successful.


View all variations within a section of a multivariate experiment
*****************************************************************

You query variations either with an experiment id and section id or with a :py:class:`SectionEntry` object.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	variations = c.get_variations('12345', '0')

or

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.get_experiment(client.ExperimentQuery('12345'))
	section = c.get_section(client.SectionQuery(experiment, 0))
	variations = c.get_variations(section)

``variations`` is a :py:class:`VariationFeed` instance. Individual variations are in the :py:attr:`VariationFeed.entry` attribute.


View a single variation within a section of a multivariate experiment
*********************************************************************

You can query a specific variation either with an experiment id, section id and variation id or with a :py:class:`SectionEntry` object and variation id. Variation ids are 0-based and there are :py:attr:`SectionEntry.num_variations.text` variations in the section.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	variations = c.get_variations('12345', '0', '0')

or

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.get_experiment(client.ExperimentQuery('12345'))
	section = c.get_section(client.SectionQuery(experiment, 0))
	variations = c.get_variations(section, '0')


Add a new variation to a section in a multivariate experiment
*************************************************************

Add a variation using a :py:class:`SectionEntry` or :py:class:`SectionQuery` object with a title and content for the variation.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	experiment = c.add_experiment(
	    exp_type='Multivariate', 
	    analytics_acct='1234567', 
	    test_url='http://www.example.com/test/url/', 
	    goal_url='http://www.example.com/goal/url/',
	    title='Test Exp 2')
	section = c.add_section(experiment, title='section1')
	orig_content = '<img src="cool.jpg" />'
	var_content = '<img src="cooler.jpg" />'
	var1 = c.add_variation(section, title='Original', content=orig_content)
	var2 = c.add_variation(section, title='Cooler', content=var_content)

``var1`` and ``var2`` are now a :class:`VariationEntry` instances. If there is an problem, :py:meth:`WebsiteOptimizerClient.add_variation` raises a :py:exc:`gdata.client.RequestError` exception.


Update a variation in a section in a multivariate experiment
************************************************************

Updating a variation is easy as long as you remember that all the attributes are actually XML tags. Typically you have to update the ``text`` attribute. 

.. note::

	**force=True** is the only way I've been able to get the REST API to actually update the variation.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	var = c.get_variation(client.VariationQuery('12345', '0', '1'))
	var.content.text = '<img src="evencooler.jpg" />'
	var = c.update(var, force=True)


Delete a variation from a section in a multivariate experiment
**************************************************************

You delete variations by passing either a URI (:py:class:`VariationQuery`\ ) or an :py:class:`VariationEntry` instance to the :py:meth:`WebsiteOptimizerClient.delete` method.

.. code-block:: python

	from gwo.websiteoptimizer import client
	c = client.WebsiteOptimizerClient()
	c.ClientLogin('yourlogin','yourpass','django-gwo')
	response = c.delete(client.VariationQuery('12345', '0', '1'))

The response is a :py:class:`httplib.HTTPResponse` instance. :py:attr:`httplib.HTTPResponse.status` should be 200 if everything was successful.
