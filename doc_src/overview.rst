Multivariate testing of dynamic pages
=====================================

Typically multivariate testing is testing multiple combinations of things on one page (the test URL), so see if they lead towards more readers getting to another page (the conversion URL). This falls apart when you want to test combinations of a template-driven site: the content and URL is variable, but the underlying template is constant. It really goes to hell when you don't care which page they go to on your site, just that they go to another page.


**Experiment**
	The test.

**Section**
	Parts of the template which will vary. Google Website Optimizer uses JavaScript to insert the content into these areas, so make sure the parts that you are testing will allow JavaScript to fill it.

**Variation**
	A bit of content for a section of an experiment. Google Website Optimizer fills this content into the section with JavaScript.