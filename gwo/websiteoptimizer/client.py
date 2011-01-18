"""
Ways of accessing the Google Website Optimizer API
"""

import gdata
import atom
from gdata.client import GDClient
from gdata.analytics.client import AnalyticsBaseQuery, AnalyticsClient
from gwo.websiteoptimizer import data as gwo_data

class ExperimentQuery(AnalyticsBaseQuery):
    """
    Query all experiments or a specific experiment
    """
    def __init__(self, exp_id=None, **kwargs):
        """
        :param exp_id: The experiment id, if a specific experiment is requested.
        :type  exp_id: None, int, str, unicode. **Default:** ``None``
        """
        self.exp_id = exp_id
        super(ExperimentQuery, self).__init__(**kwargs)
    
    @property
    def path(self):
        """
        The path section of the URI to this query
        """
        path = ['/analytics/feeds/websiteoptimizer/experiments']
        if self.exp_id:
            path.append(unicode(self.exp_id))
        return ('/'.join(path))


class SectionQuery(AnalyticsBaseQuery):
    """
    Query all sections or a specific section of an experiment
    """
    def __init__(self, experiment, section_id=None, **kwargs):
        """
        :param experiment: The experiment.
        :type  experiment: int, str, unicode or ``ExperimentEntry``
        :param section_id: The optional, 0-based id of a specific section.
        :type  section_id: int, str, or unicode
        """
        if experiment and isinstance(experiment, (int, basestring)):
            self.exp_id = unicode(experiment)
        elif experiment and isinstance(experiment, gwo_data.ExperimentEntry):
            self.exp_id = experiment.experiment_id.text
        else:
            raise Exception("SectionQuery was passed an experiment of type %s instead of an int, str or ExperimentEntry" % type(experiment))
        
        self.section_id = section_id
        super(SectionQuery, self).__init__(**kwargs)
    
    @property
    def path(self):
        """
        The path section of the URI to this query
        """
        path = [
            '/analytics/feeds/websiteoptimizer/experiments', 
            self.exp_id,
            'sections',
        ]
        if self.section_id:
            path.append(unicode(self.section_id))
        return '/'.join(path)


class VariationQuery(AnalyticsBaseQuery):
    """
    Query all variations or a specific variation of a section of an experiment
    
    In order to be flexible with the parameters, you can query variations with:
    
    * ``experiment_id`` and ``section_id`` and optionally ``variation_id`` 
    * ``section=SectionEntry`` and optionally ``variation_id``
    
    All variations of section 1 of experiment 12345::
    
        VariationQuery('12345', '1')
        VariationQuery(experiment_id='12345', section_id='1')
        VariationQuery(section1) # Assuming section1 is a SectionEntry instance
        VariationQuery(section=section1) # Assuming section1 is a SectionEntry instance
    
    Variation 0 of section 1 of experiment 12345::
    
        VariationQuery('12345', '1', '0')
        VariationQuery(experiment_id='12345', section_id='1', variation_id='0')
        VariationQuery(section1, '0') # Assuming section1 is a SectionEntry instance
        VariationQuery(section=section1, variation='0') # Assuming section1 is a SectionEntry instance
    """
    def __init__(self, *args, **kwargs):
        self.variation_id = None
        if args:
            if isinstance(args[0], gwo_data.SectionEntry):
                self.exp_id = args[0].experiment_id.text
                self.section_id = args[0].section_id.text
                if len(args) > 1:
                    self.variation_id = args[1]
            elif len(args) >= 2:
                self.exp_id = args[0]
                self.section_id = args[1]
                if len(args) > 2:
                    self.variation_id = args[2]
        if kwargs:
            if 'experiment_id' in kwargs:
                self.exp_id = unicode(kwargs.pop('experiment_id'))
                self.section_id = unicode(kwargs.pop('section_id'))
            else:
                section = kwargs.pop('section')
                self.exp_id = section.experiment_id.text
                self.section_id = section.section_id.text
            self.variation_id = kwargs.pop('variation_id', None)
        super(VariationQuery, self).__init__(**kwargs)
    
    @property
    def path(self):
        """
        The path section of the URI to this query
        """
        path = [
            '/analytics/feeds/websiteoptimizer/experiments',
            unicode(self.exp_id),
            'sections',
            unicode(self.section_id),
            'variations',
        ]
        if self.variation_id:
            path.append(unicode(self.variation_id))
        return "/".join(path)


class CombinationQuery(AnalyticsBaseQuery):
    """
    Query all combinations or a specific combination of a multivariate experiment
    """
    def __init__(self, experiment, combination_id=None, **kwargs):
        """
        :param experiment: The experiment
        :type experiment: int, str, unicode or ExperimentEntry
        :param combination_id: The optional id of a specific combination
        :type combination_id: int, str, or unicode
        """
        if experiment and isinstance(experiment, (int, basestring)):
            exp_id = unicode(experiment)
        elif experiment and isinstance(experiment, gwo_data.ExperimentEntry):
            exp_id = experiment.experiment_id.text
        else:
            raise Exception("get_combination_feed_for_exp was passed an experiment of type %s instead of an int, str or ExperimentEntry" % type(experiment))
        
        self.exp_id = exp_id
        self.combination_id = combination_id
        super(CombinationQuery, self).__init__(**kwargs)
    
    @property
    def path(self):
        """
        The path section of the URI to this query
        """
        path = [
            '/analytics/feeds/websiteoptimizer/experiments',
            self.exp_id,
            'combinations',
        ]
        if self.combination_id:
            path.append(unicode(self.combination_id))
        return "/".join(path)


class WebsiteOptimizerClient(AnalyticsClient):
    """
    Client extension for the Google Website Optimizer API service.
    """
    
    api_version = '2'
    auth_service = 'analytics'
    auth_scopes = gdata.gauth.AUTH_SCOPES['analytics']
    account_type = 'GOOGLE'
    
    def __init__(self, *args, **kwargs):
        """
        """
        super(WebsiteOptimizerClient, self).__init__(*args, **kwargs)
    
    def update(self, entry, auth_token=None, force=False, **kwargs):
        """
        Edits the entry on the server by sending the XML for this entry.

        Performs a PUT and converts the response to a new entry object with a
        matching class to the entry passed in.

        :param entry: The Atom Entry object.
        :param auth_token: Optional authentication token
        :param boolean force: Whether an update should be forced. **Default:**
                 False. 
                 
                 Normally, if a change has been made since the passed in
                 entry was obtained, the server will not overwrite the entry since
                 the changes were based on an obsolete version of the entry.
                 Setting force to True will cause the update to silently
                 overwrite whatever version is present.

        :returns: A new Entry object of a matching type to the entry which was passed in.
        """
        http_request = atom.http_core.HttpRequest()
        http_request.add_body_part(
            entry.to_string(gdata.client.get_xml_version(self.api_version)),
            'application/atom+xml')
        # Include the ETag in the request if present.
        if force:
            http_request.headers['If-Match'] = '*'
        elif hasattr(entry, 'etag') and entry.etag:
            http_request.headers['If-Match'] = entry.etag
        
        response = self.request(method='PUT', uri=entry.get_self_link().href,
                            auth_token=auth_token, http_request=http_request,
                            desired_class=entry.__class__, **kwargs)
        #entry.etag = old_etag
        return response
    
    
    def delete(self, entry_or_uri, auth_token=None, force=False, **kwargs):
        """
        Deletes the item specified by entry_or_uri.
        
        :param entry_or_uri: Either an Entry or Query object
        """
        http_request = atom.http_core.HttpRequest()
        
        # Include the ETag in the request if present.
        if force:
            http_request.headers['If-Match'] = '*'
        elif hasattr(entry_or_uri, 'etag') and entry_or_uri.etag:
            http_request.headers['If-Match'] = entry_or_uri.etag
        
        # If the user passes in a URL, just delete directly, may not work as
        # the service might require an ETag.
        if isinstance(entry_or_uri, (str, unicode, atom.http_core.Uri)):
            return self.request(method='DELETE', uri=entry_or_uri,
                            http_request=http_request, auth_token=auth_token,
                            **kwargs)
        
        return self.request(method='DELETE', uri=entry_or_uri.get_self_link().href,
                          http_request=http_request, auth_token=auth_token,
                          **kwargs)
    
    
    def get_experiments(self, feed_uri=None, auth_token=None, **kwargs):
        """
        Get all the experiments the current user has access to.
        
        :param feed_uri: The REST URI to get the feeds. Defaults to all experiments
        :type feed_uri: None, ExperimentQuery
        :returns: ``ExperimentFeed``
        """
        return self.get_feed(
            feed_uri or ExperimentQuery(),
            desired_class=gwo_data.ExperimentFeed,
            auth_token=auth_token,
            **kwargs)
    
    def get_experiment(self, feed_uri, auth_token=None, **kwargs):
        """
        Get a specific experiment.
        
        :param feed_uri: The REST URI to get the feeds
        :type feed_uri: ExperimentQuery
        :returns: ``ExperimentEntry``
        """
        if isinstance(feed_uri, gwo_data.ExperimentEntry):
            uri = feed_uri.get_self_link().href
        else:
            uri = feed_uri
        return self.get_entry(
            uri,
            desired_class=gwo_data.ExperimentEntry,
            auth_token=auth_token,
            **kwargs)
    
    def add_experiment(self, exp_type, analytics_acct, test_url, goal_url, title, **kwargs):
        """
        Create a new experiment
        
        On failure, a RequestError is raised of the form::
        
            {'status': HTTP status code from server, 
            'reason': HTTP reason from the server, 
            'body': HTTP body of the server's response}
        
        :param str exp_type: 'AB' or 'Multivariate'
        :param str analytics_acct: The Google Analytics account to use
        :param str test_url: The test page URL
        :param str goal_url: The goal page URL
        :param str title: The name of the experiment
        :returns: ExperimentEntry
        :raises: RequestError
        """
        kwargs['experiment_type'] = gwo_data.ExperimentType(text=exp_type)
        kwargs['analytics_account_id'] = gwo_data.AnalyticsAccountId(text=analytics_acct)
        kwargs['link'] = [
            gwo_data.GwoLink(href=test_url, rel='testUrl'),
            gwo_data.GwoLink(href=goal_url, rel='goalUrl')
        ]
        kwargs['title'] = atom.data.Title(text=title)
        experiment = gwo_data.ExperimentEntry(**kwargs)
        return self.post(experiment, ExperimentQuery())
    
    def start_experiment(self, feed_uri, **kwargs):
        """
        Start an experiment
        
        :param feed_uri: The REST URI to get the feeds
        :type feed_uri: ExperimentQuery
        """
        exp = self.get_experiment(feed_uri)
        exp.status.text = "Running"
        return self.update(exp, force=True)
    
    def pause_experiment(self, feed_uri, **kwargs):
        """
        Pause an experiment
        
        :param feed_uri: The REST URI to get the feeds
        :type feed_uri: ExperimentQuery
        """
        exp = self.get_experiment(feed_uri)
        exp.status.text = "Paused"
        return self.update(exp, force=True)
    
    def stop_experiment(self, feed_uri, **kwargs):
        """
        Stop an experiment
        
        :param feed_uri: The REST URI to get the feeds
        :type feed_uri: ExperimentQuery
        """
        exp = self.get_experiment(feed_uri)
        exp.status.text = "Finished"
        return self.update(exp, force=True)
    
    def get_sections(self, feed_uri, auth_token=None, **kwargs):
        """
        Get a section feed for an experiment.
        
        :param SectionQuery feed_uri: The SectionQuery from which to get the feed
        :returns: SectionFeed
        """
        return self.get_feed(
            feed_uri,
            desired_class=gwo_data.SectionFeed,
            auth_token=auth_token,
            **kwargs)
    
    def get_section(self, feed_uri, auth_token=None, **kwargs):
        """
        Get a section for an experiment.
        
        :param SectionQuery feed_uri: The SectionQuery from which to get the SectionEntry
        :returns: SectionEntry
        """
        return self.get_entry(
            feed_uri,
            desired_class=gwo_data.SectionEntry,
            auth_token=auth_token,
            **kwargs)
    
    def add_section(self, experiment, title, **kwargs):
        """
        Add a section to an experiment
        
        :param experiment: The experiment which to add the section
        :type experiment: int, str, unicode or ExperimentEntry
        :param str title: The name of the section
        """
        if isinstance(experiment, gwo_data.ExperimentEntry):
            exp_id = experiment.experiment_id.text
        else:
            exp_id = unicode(experiment)
        
        entry = gwo_data.SectionEntry(title=atom.data.Title(text=title))
        return self.post(entry, SectionQuery(exp_id))
    
    def get_variations(self, feed_uri, auth_token=None, **kwargs):
        """
        Get a variation feed for an experiment section.
        
        :param VariationQuery feed_uri: The VariationQuery from which to get the VariationFeed
        :returns: VariationFeed
        """
        return self.get_feed(
            feed_uri,
            desired_class=gwo_data.VariationFeed,
            auth_token=auth_token,
            **kwargs)
    
    def get_variation(self, feed_uri, auth_token=None, **kwargs):
        """
        Get a variation for an experiment section.
        
        :param VariationQuery feed_uri: The VariationQuery from which to get the VariationEntry
        :returns: VariationEntry
        """
        return self.get_entry(
            feed_uri,
            desired_class=gwo_data.VariationEntry,
            auth_token=auth_token,
            **kwargs)
    
    def add_variation(self, section, title, content, **kwargs):
        """
        Add a variation to an experiment section.
        
        :param section: The section which to add the variation
        :type section: SectionEntry or SectionQuery
        :param str title: The name of the variation
        :param str content: The content of the variation (what goes on the page)
        """
        if not isinstance(section, (gwo_data.SectionEntry, SectionQuery)):
            raise Exception("The section parameter needs a SectionEntry or SectionQuery instance, not a %s" % type(section))
        variation = gwo_data.VariationEntry(
            title=atom.data.Title(text=title),
            content=atom.data.Content(text=content),
        )
        if isinstance(section, SectionQuery):
            return self.post(variation, VariationQuery(section.exp_id, section.section_id))
        return self.post(variation, VariationQuery(section))
    
    def get_combinations(self, feed_uri, auth_token=None, **kwargs):
        """
        A list of all combinations in the specified experiment
        
        :param CombinationQuery feed_uri: The CombinationQuery to get all the combinations
        :returns: CombinationFeed
        """
        return self.get_feed(
            feed_uri,
            desired_class=gwo_data.CombinationFeed,
            auth_token=auth_token,
            **kwargs)
    
    def get_combination(self, feed_uri, auth_token=None, **kwargs):
        """
        Information about a single combination within an experiment
        
        :param CombinationQuery feed_uri: The CombinationQuery to specify the combination
        :returns: CombinationEntry
        """
        return self.get_entry(
            feed_uri,
            desired_class=gwo_data.CombinationEntry,
            auth_token=auth_token,
            **kwargs)
    
