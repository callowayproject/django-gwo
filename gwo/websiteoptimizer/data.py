import atom
from gdata.analytics.data import GetProperty, GaLinkFinder
from gdata.data import GDFeed, GDEntry

GWO_NS = '{http://schemas.google.com/analytics/websiteoptimizer/2009}%s'

class GWOElementClass(type):
    """
    A metaclass that sets the _qname attribute based on the class name
    """
    def __new__(mcs, classname, bases, classdict):
        if '_qname' not in classdict:
            tag_name = '%s%s' % (classname[0].lower(), classname[1:])
            qname = GWO_NS % tag_name
            classdict['_qname'] = qname
        return type.__new__(mcs, classname, bases, classdict)

class BaseGWOElement(atom.core.XmlElement):
    """
    Base class that sets the metaclass
    """
    __metaclass__ = GWOElementClass

class ExperimentId(BaseGWOElement):
    """
    the experiment ID for this experiment (read-only)
    """
    pass

class ExperimentType(BaseGWOElement):
    """
    the experiment type: AB or Multivariate. 
    (read-only; may be set during experiment creation)
    """
    pass

class ExperimentNotes(BaseGWOElement):
    """
    user-created notes field. Limited to 2000 characters.
    """
    pass

class AnalyticsAccountId(BaseGWOElement):
    """
    the account ID that owns this experiment. 
    (read-only; may be set during experiment creation)
    """
    pass

class Status(BaseGWOElement):
    """
    the current status of the experiment: New, Running, Paused, or Finished.
    """
    pass

class Coverage(BaseGWOElement):
    """
    the percentage of total traffic to include in the experiment.
    """
    pass

class NumAbPageVariations(BaseGWOElement):
    """
    the number of page variations in this experiment (A/B experiments only). 
    (read-only)
    """
    pass

class NumSections(BaseGWOElement):
    """
    the number of sections in the experiment (multivariate experiments only). 
    (read-only)
    """
    pass

class NumCombinations(BaseGWOElement):
    """
    the number of combinations in the experiment. 
    (read-only)
    """
    pass

class SourceExperimentId(BaseGWOElement):
    """
    the experiment ID of which this experiment is a copy or follow-up. 
    (read-only; may be set during experiment creation)
    """
    pass

class VerificationCombo(BaseGWOElement):
    """
    for follow-up experiments, the combination being verified against the original. 
    (read-only; may be set during experiment creation)
    """
    pass

class VerificationComboCoverage(BaseGWOElement):
    """
    for follow-up experiments, the percentage of traffic to send to the verification combo. 
    (read-only, may be set during experiment creation)
    """
    pass

class AutoPruneMode(BaseGWOElement):
    """
    the auto-prune setting for this experiment: None, Conservative, Normal or Aggressive. 
    """
    pass

class ControlScript(BaseGWOElement):
    """
    the control script that should be placed at the top of any webpage in this experiment. 
    (read-only)
    """
    pass

class TrackingScript(BaseGWOElement):
    """
    the tracking script that should be placed at the bottom of any webpage in this experiment. 
    (read-only)
    """
    pass

class ConversionScript(BaseGWOElement):
    """
    the conversion script that should be called when a visitor converts.
    (read-only)
    """
    pass

class GwoLink(atom.data.Link):
    """
    A link with the gwo namespace
    """
    xmlns_gwo = 'xmlns:gwo'
    
    def __init__(self, *args, **kwargs):
        if 'xmlns_gwo' not in kwargs:
            kwargs['xmlns_gwo'] = 'http://schemas.google.com/analytics/websiteoptimizer/2009'
        if 'type' not in kwargs:
            kwargs['type'] = 'text/html'
        if 'rel' in kwargs and not kwargs['rel'].startswith('gwo:'):
            kwargs['rel'] = 'gwo:%s' % kwargs['rel']
        super(GwoLink, self).__init__(*args, **kwargs)

# class GoalUrl(BaseGWOElement, atom.data.Link):
#     """
#     The test page URL for display in Website Optimizer UI.
#     """
#     pass

class SectionId(BaseGWOElement):
    """
    the id for this section (0-based). (read-only)
    """
    pass

class NumVariations(BaseGWOElement):
    """
    the number of variations for this section. (read-only)
    """
    pass

class SectionBeginScript(BaseGWOElement):
    """
    the script snippet to place before this section. (read-only)
    """
    pass

class SectionEndScript(BaseGWOElement):
    """
    the script snippet to place after this section (read-only)
    """
    pass

class VariationId(BaseGWOElement):
    """
    the id for this variation (0-based). (read-only)
    """
    pass

class ComboId(BaseGWOElement):
    """
    the id of this combination (0-based; read-only)
    """
    pass

class ComboString(BaseGWOElement):
    """
    the combination info string, which consists of a set of variation indices 
    for each section. For example, 0-1-1. (read-only)
    """
    pass

class ComboActive(BaseGWOElement):
    """
    true if the combination is active; false if it has been pruned.
    """
    pass

class GwoLinkFinder(GaLinkFinder):
    """
    Locates the various links within the ExperimentsEntry
    """
    def get_test_link(self):
        """
        the test page URL (as entered by the user) for display in Website Optimizer UI. 
        """
        return self.find_url('gwo:testUrl')
    
    def get_goal_link(self):
        """
        the goal page url (as entered by user) for display in Website Optimizer UI.
        """
        return self.find_url('gwo:goalUrl')
    
    def get_report_url(self):
        """
        the link to the report page for the experiment. (read-only)
        """
        return self.find_url('gwo:reportUrl')
    
    def get_configuration_url(self):
        """
        the link to the configuration page for the experiment. (read-only)
        """
        return self.find_url('gwo:configurationUrl')


class ExperimentEntry(GDEntry, GetProperty, GwoLinkFinder):
    """
    An experiment on Google Website Optimizer
    """
    id = atom.data.Id
    title = atom.data.Title
    experiment_id = ExperimentId
    experiment_type = ExperimentType
    experiment_notes = ExperimentNotes
    analytics_account_id = AnalyticsAccountId
    status = Status
    coverage = Coverage
    num_ab_page_variations = NumAbPageVariations
    num_sections = NumSections
    num_combinations = NumCombinations
    source_experiment_id = SourceExperimentId
    verification_combo = VerificationCombo
    verification_combo_coverage = VerificationComboCoverage
    auto_prune_mode = AutoPruneMode
    control_script = ControlScript
    tracking_script = TrackingScript
    conversion_script = ConversionScript
    
    def update_test_link(self, url):
        """
        Convenience method for changing the testUrl
        
        :param str url: The new testing URL
        """
        
        for item in self.link:
            if item.rel == 'gwo:testUrl':
                item.href = url
                break
    
    def update_goal_link(self, url):
        """
        Convenience function for changing the goalUrl
        
        :param str url: The new goal URL
        """
        for item in self.link:
            if item.rel == 'gwo:goalUrl':
                item.href = url
                break
    

class ExperimentFeed(GDFeed):
    """Web Optimizer Experiments Feed <feed>"""
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [ExperimentEntry]


class SectionEntry(GDEntry, GetProperty):
    _qname = atom.data.ATOM_TEMPLATE % 'entry'
    
    id = atom.data.Id
    title = atom.data.Title
    experiment_id = ExperimentId
    section_id = SectionId
    num_variations = NumVariations
    section_begin_script = SectionBeginScript
    section_end_script = SectionEndScript


class SectionFeed(GDFeed):
    """
    All of the sections for a multivariate experiment
    """
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [SectionEntry]


class VariationEntry(GDEntry, GetProperty):
    """
    A variation for a specific section of a specific experiment
    """
    _qname = atom.data.ATOM_TEMPLATE % 'entry'
    
    id = atom.data.Id
    experiment_id = ExperimentId
    section_id = SectionId
    variation_id = VariationId
    content = atom.data.Content


class VariationFeed(GDFeed):
    """
    All the variations for a specific section of a specific experiment
    """
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [VariationEntry]


class CombinationEntry(GDEntry, GetProperty):
    """
    A combination in the specified experiment
    """
    _qname = atom.data.ATOM_TEMPLATE % 'entry'
    
    id = atom.data.Id
    experiment_id = ExperimentId
    combo_id = ComboId
    combo_string = ComboString
    combo_active = ComboActive


class CombinationFeed(GDFeed):
    """
    A list of all combinations in the specified experiment
    """
    _qname = atom.data.ATOM_TEMPLATE % 'feed'
    entry = [CombinationEntry]
