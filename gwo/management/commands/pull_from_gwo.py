from django.core.management.base import NoArgsCommand, CommandError
from gwo.websiteoptimizer import client
from gwo.models import GwoExperiment, GwoSection, GwoVariation

class Command(NoArgsCommand):
    help = "Pull experiment data from Google Website Optimizer"
    can_import_settings = True
    
    @property
    def client(self):
        from gwo.settings import GWO_PASSWORD, GWO_USER
        
        if not hasattr(self, "_client"):
            gwo_client = client.WebsiteOptimizerClient()
            gwo_client.ClientLogin(GWO_USER, GWO_PASSWORD, 'django-gwo')
            self._client = gwo_client
        
        return self._client

    def create_variation(self, var_obj, section):
        print "    Building variation %s" % var_obj.title.text
        var = GwoVariation(
            gwo_experiment=section.gwo_experiment,
            gwo_section=section,
            title=getattr(var_obj.title, 'text', ''),
            variation_id=getattr(var_obj.variation_id, 'text', ''),
            content=getattr(var_obj.content, 'text', ''),
        )
        var.save(local_only=True)
    
    def create_section(self, section_obj, experiment):
        print "   Building section %s" % section_obj.title.text
        sec = GwoSection(
            gwo_experiment=experiment,
            title=getattr(section_obj.title, 'text', ''),
            begin_script=getattr(section_obj.section_begin_script, 'text', ''),
            end_script=getattr(section_obj.section_end_script, 'text', ''),
            section_id=getattr(section_obj.section_id, 'text', ''),
        )
        sec.save(local_only=True)
        
        print "   Pulling Variations"
        var_feed = self.client.get_variations(client.VariationQuery(section_obj))
        
        for var_obj in var_feed.entry:
            self.create_variation(var_obj, sec)
    
    def create_experiment(self, exp_obj):
        print "  Building experiment %s" % exp_obj.title.text
        expr = dict(
            title=exp_obj.title.text,
            experiment_id=getattr(exp_obj.experiment_id, 'text', ''),
            experiment_type=exp_obj.experiment_type.text,
            control_script=getattr(exp_obj.control_script, 'text', ''),
            tracking_script=getattr(exp_obj.tracking_script, 'text', ''),
            conversion_script=getattr(exp_obj.conversion_script, 'text', ''),
            status=getattr(exp_obj.status, 'text', 'New'),
            auto_prune_mode=getattr(exp_obj.auto_prune_mode, 'text', 'None'),
            test_url=exp_obj.get_test_link() or '',
            goal_url=exp_obj.get_goal_link() or ''
        )
        
        exp = GwoExperiment(**expr)
        exp.save(local_only=True)
        print "  Pulling sections"
        section_feed = self.client.get_sections(client.SectionQuery(exp_obj.experiment_id.text))
        for sum_section_obj in section_feed.entry:
            section_obj = self.client.get_section(sum_section_obj.get_self_link().href)
            self.create_section(section_obj, exp)
    
    def sync_variation(self, var_obj, section):
        try:
            var = GwoVariation.objects.get(
                gwo_experiment=section.gwo_experiment,
                gwo_section=section,
                variation_id=var_obj.variation_id.text
            )
            created = False
        except GwoVariation.DoesNotExist:
            var = GwoVariation(
                gwo_experiment=section.gwo_experiment,
                gwo_section=section,
                variation_id=var_obj.variation_id.text
            )
            created = True
        
        if created:
            print "    Building variation %s" % var_obj.title.text
        else:
            print "    Updating variation %s" % var_obj.title.text
        
        var.title = var_obj.title.text
        var.content = getattr(var_obj.content, 'text', '')
        var.save(local_only=True)
    
    def sync_section(self, section_obj, exp_obj):
        try:
            section = GwoSection.objects.get(
                gwo_experiment=exp_obj,
                section_id=section_obj.section_id.text
            )
            created = False
        except GwoSection.DoesNotExist:
            section = GwoSection(
                gwo_experiment=exp_obj,
                section_id=section_obj.section_id.text
            )
            created = True
        if created:
            print "   Building section %s" % section_obj.title.text
        else:
            print "   Updating section %s" % section_obj.title.text
        
        section.title = section_obj.title.text
        section.begin_script = getattr(section_obj.section_begin_script, 'text', '')
        section.end_script = getattr(section_obj.section_end_script, 'text', '')
        section.save(local_only=True)
        
        print "   Pulling Variations"
        try:
            var_feed = self.client.get_variations(client.VariationQuery(section_obj))
        except Exception, e:
            print "   Error pulling variations"
            return
        
        gwo_vars = []
        for var_obj in var_feed.entry:
            self.sync_variation(var_obj, section)
            gwo_vars.append(int(var_obj.variation_id.text))
        
        variations = set(section.gwovariation_set.all().values_list('variation_id', flat=True))
        deleteable = variations - set(gwo_vars)
        section.gwovariation_set.filter(variation_id__in=list(deleteable)).delete()
    
    def sync_experiment(self, exp_obj):
        try:
            experiment = GwoExperiment.objects.get(
                experiment_id=exp_obj.experiment_id.text
            )
            created = False
        except GwoExperiment.DoesNotExist:
            experiment = GwoExperiment(experiment_id=exp_obj.experiment_id.text)
            created = False
        if created:
            print "  Building experiment %s" % exp_obj.title.text
        else:
            print "  Updating experiment %s" % exp_obj.title.text
        expr = dict(
            title=exp_obj.title.text,
            experiment_id=getattr(exp_obj.experiment_id, 'text', ''),
            experiment_type=exp_obj.experiment_type.text,
            control_script=getattr(exp_obj.control_script, 'text', ''),
            tracking_script=getattr(exp_obj.tracking_script, 'text', ''),
            conversion_script=getattr(exp_obj.conversion_script, 'text', ''),
            status=getattr(exp_obj.status, 'text', 'New'),
            auto_prune_mode=getattr(exp_obj.auto_prune_mode, 'text', 'None'),
            test_url=exp_obj.get_test_link() or '',
            goal_url=exp_obj.get_goal_link() or ''
        )
        
        for key, val in expr.items():
            setattr(experiment, key, val)
        
        experiment.save(local_only=True)
        print "  Pulling sections"
        try:
            section_feed = self.client.get_sections(client.SectionQuery(exp_obj.experiment_id.text))
        except Exception, e:
            print "  Error getting sections"
            return
        gwo_sections = []
        for sum_section_obj in section_feed.entry:
            section_obj = self.client.get_section(sum_section_obj.get_self_link().href)
            self.sync_section(section_obj, experiment)
            gwo_sections.append(int(section_obj.section_id.text))
        
        sections = set(experiment.gwosection_set.all().values_list('section_id', flat=True))
        deleteable = sections - set(gwo_sections)
        experiment.gwosection_set.filter(section_id__in=list(deleteable)).delete()
    
    def handle_noargs(self, **options):
        """
        Main entry point.
        """
        
        # Experiments could have been deleted through GWO. Delete anything
        # that has previously saved to GWO and start fresh
        # print "Purging local experiments"
        # GwoExperiment.objects.filter(experiment_id__isnull=False).delete()
        print "Pulling experiments from Google Website Optimizer"
        exp_feed = self.client.get_experiments()
        gwo_exps = []
        for summary_exp in exp_feed.entry:
            exp = self.client.get_experiment(summary_exp.get_self_link().href)
            self.sync_experiment(exp)
            gwo_exps.append(int(exp.experiment_id.text))
        
        exps = set(GwoExperiment.objects.all().values_list('experiment_id', flat=True))
        deleteable = exps - set(gwo_exps)
        GwoExperiment.objects.filter(experiment_id__in=list(deleteable)).delete()
        