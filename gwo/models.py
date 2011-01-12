from django.db import models

import settings

EXPERIMENT_STATUSES = (
    (1, 'New'),
    (2, 'Running'), 
    (3, 'Paused'), 
    (4, 'Finished'),
)
AUTO_PRUNE_MODES = (
    (0, 'None'),
    (1, 'Conservative'),
    (2, 'Normal'),
    (3, 'Aggressive'),
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
