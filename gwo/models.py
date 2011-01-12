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
        help_text="This is the ID assigned by Google Website Optimizer.",
    )
    experiment_type = models.CharField(choices=(('AB', 'A/B Test'), ('Multivariate', 'Multivariate')), max_length=15)
    control_script = models.TextField(blank=True)
    tracking_script = models.TextField(blank=True)
    conversion_script = models.TextField(blank=True)
    status = models.CharField(default='New', max_length=10, blank=True)
    auto_prune_mode = models.IntegerField(choices=AUTO_PRUNE_MODES, default=0)
    test_url = models.URLField(
        verbose_name="Test page URL",
        verify_exists=False,
        max_length=255, 
        help_text="When testing dynamic pages, select use a URL that uses the template being tested"
    )
    goal_url = models.URLField(
        verbose_name="Coversion page URL",
        verify_exists=False,
        max_length=255,
        help_text="This can be the same as the testing URL. You can trigger a 'conversion' via JavaScript."
    )
    report_url = models.URLField(max_length=255, blank=True)
    configuration_url = models.URLField(max_length=255, blank=True)
    
    class Meta:
        pass
    
    def __unicode__(self):
        return self.title
    
    def _sync_gwo_experiment(self):
        """
        Automatically called by the save method
        """
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.experiment_id:
            exp = gwo_client.get_experiment(client.ExperimentQuery(self.experiment_id))
            exp.title.text = self.title
            exp.auto_prune_mode.text = self.auto_prune_mode
            exp.update_test_link = self.test_url
            exp.update_goal_link = self.goal_url
            gwo_client.update(exp, force=True)
        else:
            exp = gwo_client.add_experiment(
                exp_type=self.experiment_type, 
                analytics_acct=settings.GWO_ACCOUNT, 
                test_url=self.test_url, 
                goal_url=self.test_url,
                title=self.title,
            )
            self.experiment_id = exp.experiment_id.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        """
        self._sync_gwo_experiment()
        super(GwoExperiment, self).save(*args, **kwargs)

class GwoSection(models.Model):
    """
    A section within a multivariate GWO experiment
    """
    gwo_experiment = models.ForeignKey(GwoExperiment, verbose_name="Experiment")
    section_id = models.IntegerField(
        "GWO Section ID", 
        blank=True, 
        null=True,
        help_text="This is the ID assigned by Google Website Optimizer.",
    )
    title = models.CharField(max_length=100)
    
    class Meta:
        pass

    def __unicode__(self):
        return u"%s Section: %s" % (self.gwo_experiment, self.title)
    
    def _sync_gwo_section(self):
        """
        Automatically called by the save method
        """
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.section_id:
            sec_qry = client.SectionQuery(
                self.gwo_experiment.experiment_id, 
                self.section_id
            )
            sec = gwo_client.get_section(sec_qry)
            sec.title.text = self.title
            gwo_client.update(sec, force=True)
        else:
            sec = gwo_client.add_section(
                self.gwo_experiment.experiment_id,  
                title=self.title,
            )
            self.section_id = sec.section_id.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        """
        self._sync_gwo_section()
        super(GwoSection, self).save(*args, **kwargs)


class GwoVariation(models.Model):
    """
    A variation of a section within a multivariate experiment
    """
    gwo_experiment = models.ForeignKey(GwoExperiment)
    gwo_section = models.ForeignKey(GwoSection)
    variation_id = models.IntegerField(
        "GWO Variation ID",
        blank=True, 
        null=True,
        help_text="This is the ID assigned by Google Website Optimizer.",
    )
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    class Meta:
        pass

    def __unicode__(self):
        return u"%s Variation: %s" % (self.gwo_section, self.title)
    
    def _sync_gwo_variation(self):
        """
        Automatically called by the save method
        """
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.variation_id:
            var_qry = client.VariationQuery(
                self.gwo_experiment.experiment_id, 
                self.gwo_section.section_id,
                self.variation_id
            )
            var = gwo_client.get_variation(var_qry)
            var.title.text = self.title
            var.content.text = self.content
            gwo_client.update(var, force=True)
        else:
            sec_qry = client.SectionQuery(
                self.gwo_experiment.experiment_id, 
                self.gwo_section.section_id
            )
            var = gwo_client.add_variation(
                sec_qry,  
                title=self.title,
                content=self.content
            )
            self.variation_id = var.variation_id.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        """
        self._sync_gwo_variation()
        super(GwoSection, self).save(*args, **kwargs)
    
        