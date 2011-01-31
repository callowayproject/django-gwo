from django.db import models

import settings

AUTO_PRUNE_MODES = (
    ('None', 'None'),
    ('Conservative', 'Conservative'),
    ('Normal', 'Normal'),
    ('Aggressive', 'Aggressive'),
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
    auto_prune_mode = models.CharField(choices=AUTO_PRUNE_MODES, max_length='15', default='None')
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
    
    @property
    def gwo_url(self):
        """
        Return the URL represented by the GwoExperimentQuery
        """
        from websiteoptimizer import client
        return client.ExperimentQuery(self.experiment_id)
    
    def _sync_gwo_experiment(self):
        """
        Automatically called by the save method
        """
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.experiment_id:
            exp = gwo_client.get_experiment(self.gwo_url)
            exp.title.text = self.title
            # Google doesn't like it if we change the auto_prune_mode
            # exp.auto_prune_mode.text = self.auto_prune_mode
            exp.update_test_link = self.test_url
            exp.update_goal_link = self.goal_url
            exp = gwo_client.update(exp, force=True)
        else:
            exp = gwo_client.add_experiment(
                exp_type=self.experiment_type, 
                analytics_acct=settings.GWO_ACCOUNT, 
                test_url=self.test_url, 
                goal_url=self.test_url,
                title=self.title,
            )
            self.experiment_id = exp.experiment_id.text
        
        self.control_script = exp.control_script.text
        self.tracking_script = exp.tracking_script.text
        self.conversion_script = exp.tracking_script.text
        self.status = exp.status.text
        # self.report_url = exp.report_url.text
        # self.configuration_url = exp.configuration_url.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        
        The local_only=True keyword argument will prevent syncing the item with
        Google Website Optimizer's API
        """
        if not kwargs.pop('local_only', False):
            self._sync_gwo_experiment()
        super(GwoExperiment, self).save(*args, **kwargs)

class GwoAbPageVariation(models.Model):
    """
    A Page Variation in an A/B Experiment
    """
    gwo_experiment = models.ForeignKey(
        GwoExperiment, 
        verbose_name="Experiment",
        limit_choices_to={'experiment_type':'AB'})
    appagevariation_id = models.IntegerField(
        "GWO AB Page Variation ID", 
        blank=True, 
        null=True,
        help_text="This is the ID assigned by Google Website Optimizer.",
    )
    title = models.CharField(max_length=100)
    content = models.URLField("Page URL", verify_exists=False)
    
    class Meta:
        pass
    
    def __unicode__(self):
        return self.title

class GwoSection(models.Model):
    """
    A section within a multivariate GWO experiment
    """
    gwo_experiment = models.ForeignKey(
        GwoExperiment, 
        verbose_name="Experiment",
        limit_choices_to={'experiment_type': 'Multivariate'})
    section_id = models.IntegerField(
        "GWO Section ID", 
        blank=True, 
        null=True,
        help_text="This is the ID assigned by Google Website Optimizer.",
    )
    title = models.CharField(max_length=100)
    begin_script = models.CharField(blank=True, max_length=255)
    end_script = models.CharField(blank=True, max_length=255)
    
    class Meta:
        pass

    def __unicode__(self):
        return u"%s Section: %s" % (self.gwo_experiment, self.title)
    
    @property
    def gwo_url(self):
        """
        Return the URL represented by the GwoExperimentQuery
        """
        from websiteoptimizer import client
        return client.SectionQuery(
            self.gwo_experiment.experiment_id, 
            self.section_id
        )
    
    def _sync_gwo_section(self):
        """
        Automatically called by the save method
        """
        if self.gwo_experiment is None:
            return
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.section_id:
            sec = gwo_client.get_section(self.gwo_url)
            sec.title.text = self.title
            sec = gwo_client.update(sec, force=True)
        else:
            sec = gwo_client.add_section(
                self.gwo_experiment.experiment_id,  
                title=self.title,
            )
        self.section_id = sec.section_id.text
        self.begin_script = sec.section_begin_script.text
        self.end_script = sec.section_end_script.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        
        The local_only=True keyword argument will prevent syncing the item with
        Google Website Optimizer's API
        """
        if not kwargs.pop('local_only', False):
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
    
    @property
    def gwo_url(self):
        """
        Return the URL represented by the GwoExperimentQuery
        """
        from websiteoptimizer import client
        return client.VariationQuery(
            self.gwo_experiment.experiment_id, 
            self.gwo_section.section_id,
            self.variation_id
        )
    
    def _sync_gwo_variation(self):
        """
        Automatically called by the save method
        """
        from websiteoptimizer import client
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        if self.variation_id:
            var = gwo_client.get_variation(self.gwo_url)
            var.title.text = self.title
            var.content.text = self.content
            gwo_client.update(var, force=True)
        else:
            var = gwo_client.add_variation(
                self.gwo_section.gwo_url,  
                title=self.title,
                content=self.content
            )
            self.variation_id = var.variation_id.text
    
    def save(self, *args, **kwargs):
        """
        Sync with Google Website Optimizer
        
        The local_only=True keyword argument will prevent syncing the item with
        Google Website Optimizer's API
        """
        from django.core.exceptions import ValidationError
        if self.gwo_experiment != self.gwo_section.gwo_experiment:
            raise ValidationError("The experiment and the section don't go together!")
        if not kwargs.pop('local_only', False):
            self._sync_gwo_variation()
        super(GwoVariation, self).save(*args, **kwargs)

def handle_delete(sender, instance, **kwargs):
    """
    Send out a delete to GWO
    """
    from websiteoptimizer import client
    gwo_client = client.WebsiteOptimizerClient()
    gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
    
    gwo_client.delete(instance.gwo_url)

# from django.db.models.signals import pre_delete
# pre_delete.connect(handle_delete, sender=GwoExperiment)
# pre_delete.connect(handle_delete, sender=GwoSection)
# pre_delete.connect(handle_delete, sender=GwoVariation)