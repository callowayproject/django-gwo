from django.db import models

EXPERIMENT_STATUSES = (
    ('New', 1),
    ('Running', 2), 
    ('Paused', 3), 
    ('Finished', 4),
)
AUTO_PRUNE_MODES = (
    ('None', 0),
    ('Conservative', 1),
    ('Normal', 2),
    ('Aggressive', 3),
)


class GwoExperiment(models.Model):
    """An experiment or test in Google Website Optimizer"""
    title = models.CharField(max_length=100)
    experiment_id = models.IntegerField(
        "GWO Experiment ID", 
        blank=True, 
        null=True,
        help_text="This is the ID assigned by Google Website Optimizer and will automatically parsed from the scripts.",
    )
    control_script = models.TextField(blank=True)
    tracking_script = models.TextField(blank=True)
    conversion_script = models.TextField(blank=True)
    status = models.IntegerField(choices=EXPERIMENT_STATUSES, default=1)
    auto_prune_mode = models.IntegerField(choices=EXPERIMENT_STATUSES, default=0)
    test_url = models.URLField(max_length=255)
    goal_url = models.URLField(max_length=255)
    report_url = models.URLField(max_length=255)
    configuration_url = models.URLField(max_length=255)
    
    class Meta:
        pass
    
    def __unicode__(self):
        return "Experiment: %s" % self.title
    
    def _create_gwo_experiment(self):
        from gdata.analytics.service import AnalyticsDataService
        client = AnalyticsDataService()
        client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD)
    

class GwoSection(models.Model):
    """A section within a multivariate GWO experiment"""
    gwo_experiment = models.ForeignKey(GwoExperiment)
    section_id = models.IntegerField(blank=True)
    title = models.CharField(max_length=100)
    
    class Meta:
        pass

    def __unicode__(self):
        return u"%s Section: %s" % (self.gwo_experiment, self.title)

class GwoVariation(models.Model):
    """A variation of a section within a multivariate experiment"""
    gwo_experiment = models.ForeignKey(GwoExperiment)
    gwo_section = models.ForeignKey(GwoSection)
    variation_id = models.IntegerField(blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s Variation: %s" % (self.gwo_section, self.title)
