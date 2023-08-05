from plone.memoize.instance import memoize
from zope.component import getAllUtilitiesRegisteredFor, queryMultiAdapter, getSiteManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import DirectoryExportContext
from Products.GenericSetup.interfaces import IBody
import tempfile, tarfile
from Products.Archetypes.Field import *
import os, sys, platform
from Products.GenericSetup.utils import exportObjects
from controlpanel import plone_shipped_workflows
import logging

logger = logging.getLogger("uwosh.northstar.generator")

HAS_PLONEFORMGEN_INSTALLED = True

try:
    from Products.PloneFormGen.content.fields import *
    from Products.PloneFormGen.content.likertField import LikertField
    from Products.PloneFormGen.interfaces.form import IPloneFormGenForm
    
    field_type_mapping = {    
        PlainTextField : 'string',
        NRBooleanField : 'boolean',
        LinesVocabularyField : 'lines',
        HtmlTextField : 'text',
        StringVocabularyField : 'string',
        StringField : 'string',
        DateTimeField : 'datetime',
        FixedPointField : 'fixedpoint',
        FileField : 'file',
        LinesField : 'lines',
        LikertField : 'cmfobject',
        IntegerField : 'integer',
    }
    
except:
    HAS_PLONEFORMGEN_INSTALLED = False

HAS_DEXTERITY_INSTALLED = True
try:
    from plone.dexterity.interfaces import IDexterityFTI
    from zope import schema
    from plone.namedfile import field as namedfile
    from z3c.relationfield.schema import RelationChoice, RelationList
    from plone.formwidget.contenttree import ObjPathSourceBinder
    
    field_type_mapping = {
        schema.Bool : 'boolean',
        schema.TextLine : 'textline',
        schema.Text : 'richtext',
        schema.Text : 'text',
        schema.Password : 'password',
        schema.Int : 'int',
        schema.Float : 'float',
        schema.Date : 'date',
        schema.Datetime : 'datetime',
        namedfile.NamedFile : 'file',
        namedfile.NamedBlobFile : 'blobfile',
        namedfile.NamedImage : 'image',
        namedfile.NamedBlobImage : 'blobimage',
        RelationChoice : 'relation',
        RelationList : 'relationlist'
    }
    
except:
    HAS_DEXTERITY_INSTALLED = False
    
HAS_ZOPESKEL_DEXTERITY_INSTALLED = True
try:
    from zopeskel.dexterity import *
except:
    HAS_ZOPESKEL_DEXTERITY_INSTALLED = False
    

HAS_ZOPESKEL_INSTALLED = True
try:
#if True:
    from zopeskel.localcommands import ZopeSkelLocalCommand
#    from zopeskel import localcommands
    from paste.script.create_distro import CreateDistroCommand
    from paste.script import pluginlib, copydir
    
    class DistroCommand(CreateDistroCommand):

        verbose = False
        no_interactive = True
        simulate = False
        overwrite = True
        interactive = False

        def run(self, args, options):
            self.parse_args(args)
            self.options.overwrite = True
            self.options.simulate = False
            self.options.interactive = False
            self.options.verbose = False
            self.options.no_interactive = True
            return self.command(options)

        def command(self, options):
            templates = []
            for tmpl_name in self.options.templates:
                self.extend_templates(templates, tmpl_name)

            dist_name = self.args[0].lstrip(os.path.sep)

            templates = [tmpl for name, tmpl in templates]
            output_dir = os.path.join(self.options.output_dir, dist_name)

            vars = self.parse_vars(self.args[1:])
            vars.update(options)

            copydir.all_answer = 'y'

            for template in templates[::-1]:
                vars = template.check_vars(vars, self)

            egg_plugins = set(['ZopeSkel'])
            vars['egg_plugins'] = egg_plugins

            for template in templates:
                self.create_template(template, output_dir, vars)

            found_setup_py = False
            paster_plugins_mtime = None
            if os.path.exists(os.path.join(output_dir, 'setup.py')):
                # Grab paster_plugins.txt's mtime; used to determine if the
                # egg_info command wrote to it
                try:
                    egg_info_dir = pluginlib.egg_info_dir(output_dir, dist_name)
                except IOError:
                    egg_info_dir = None
                if egg_info_dir is not None:
                    plugins_path = os.path.join(egg_info_dir, 'paster_plugins.txt')
                    if os.path.exists(plugins_path):
                        paster_plugins_mtime = os.path.getmtime(plugins_path)

                self.run_command(sys.executable, 'setup.py', 'egg_info',
                                 cwd=output_dir,
                                 # This shouldn't be necessary, but a bug in setuptools 0.6c3 is causing a (not entirely fatal) problem that I don't want to fix right now:
                                 expect_returncode=True)
                found_setup_py = True

            package_dir = vars.get('package_dir', None)
            if package_dir:
                output_dir = os.path.join(output_dir, package_dir)

            # With no setup.py this doesn't make sense:
            if found_setup_py:
                # Only write paster_plugins.txt if it wasn't written by
                # egg_info (the correct way). leaving us to do it is
                # deprecated and you'll get warned
                egg_info_dir = pluginlib.egg_info_dir(output_dir, dist_name)
                plugins_path = os.path.join(egg_info_dir, 'paster_plugins.txt')
                if len(egg_plugins) and (not os.path.exists(plugins_path) or \
                        os.path.getmtime(plugins_path) == paster_plugins_mtime):
                    for plugin in egg_plugins:
                        if self.verbose:
                            print 'Adding %s to paster_plugins.txt' % plugin
                        if not self.simulate:
                            pluginlib.add_plugin(egg_info_dir, plugin)
                            
except:
    HAS_ZOPESKEL_INSTALLED = False
    

class BaseGenerator(object):
    
    create_command = None
    
    def __init__(self, view):
        self.view = view
        self.context = view.context
        self.request = view.request
    
    def paster(self, cmd, cmdplugin=None, template_vars={}):
        from paste.script import command
        args = cmd.split()
        options, args = command.parser.parse_args(args)
        options.base_parser = command.parser
        command.system_plugins.extend(options.plugins or [])
        cmmds = command.get_commands()
        command_name = args[0]
        if cmdplugin:
            runner = cmdplugin(command_name)
        else:
            command = cmmds[command_name].load()
            runner = command(command_name)
        if hasattr(runner, 'template_vars'):
            runner.template_vars.update(template_vars)
        runner.run(args[1:])
    
    @property
    @memoize
    def portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow')
    
    @property
    @memoize
    def workflows(self):
        ids = self.portal_workflow.listWorkflows()
        return [self.portal_workflow[id] for id in sorted(ids)]
    
    @property
    @memoize
    def dotted_namespace(self):
        return self.namespace_package + '.' + self.contained_namespace_package
    
    @property
    @memoize
    def namespace_package(self):
        return self.request.get('namespace-package')
        
    @property
    @memoize
    def contained_namespace_package(self):
        return self.request.get('contained-namespace-package')

class PloneFormGenTypeGenerator(BaseGenerator):
    
    create_command = "archetype"
        
    @property
    @memoize
    def types(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog.searchResults(object_provides=IPloneFormGenForm.__identifier__)
        return res
        
    def generate_type(self, type_):
        name = type_.Title().replace(' ', '').replace('-', '')
        self.paster('addcontent contenttype --no-interactive', 
            cmdplugin=ZopeSkelLocalCommand, template_vars={
                'contenttype_classname' : name,
                'contenttype_name' : name,
                'contenttype_description' : type_.Description(),
                'add_permission_name' : '%s: add %s' % (self.dotted_namespace, name),
                'schema_name' : '%sSchema' % name,
                'package_dotted_name' : self.dotted_namespace
            }
        )

        for field in type_.fgFields():
            fieldobj = type_.findFieldObjectByName(field.__name__)
            if fieldobj:
                self.paster('addcontent atschema --no-interactive', 
                    cmdplugin=ZopeSkelLocalCommand, template_vars={
                        'content_class_filename' : name.lower(),
                        'field_name' : field.__name__.replace('-', '').replace(' ', ''),
                        'field_type' : field_type_mapping[field.__class__],
                        'field_label' : fieldobj.Title(),
                        'field_desc' : fieldobj.Description(),
                        'required' : str(field.required),
                        'default' : field.default
                    }
                )

    def generate(self):
        selected_types = []
        for type_ in self.types:
            if 'export-' + type_.UID in self.request:
                type_ = type_.getObject()
                workflow_id = self.request.get('workflow-%s' % type_.UID())
                selected_types.append((type_.Title().replace(' ', '').replace('-', ''), workflow_id))
                self.generate_type(type_)
                
        
        return selected_types

class DexterityTypeGenerator(BaseGenerator):
    
    create_command = "dexterity"

    @property
    @memoize
    def types(self):
        return getAllUtilitiesRegisteredFor(IDexterityFTI)

    def get_workflow_for(self, type_):
        try:
            return self.portal_workflow.getChainForPortalType(type_.id)[0]
        except:
            return None

    def generate_type(self, type_):
        if HAS_ZOPESKEL_DEXTERITY_INSTALLED:
            self.paster('addcontent dexterity_content --no-interactive', 
                cmdplugin=ZopeSkelLocalCommand, template_vars={
                    'contenttype_name' : type_.id,
                    'contenttype_description' : type_.description,
                    'package_dotted_name' : self.dotted_namespace
                }
            )

            schema = type_.lookupSchema()
            for fieldname in schema.names():
                field = schema[fieldname]
                self.paster('addcontent dexterity_content_field --no-interactive', 
                    cmdplugin=ZopeSkelLocalCommand, template_vars={
                        'content_class_filename' : type_.id,
                        'field_name' : field.__name__,
                        'field_type' : field_type_mapping[field.__class__],
                        'field_label' : field.title,
                        'field_desc' : field.description,
                        'required' : str(field.required),
                        'default' : field.default
                    }
                )
        else:
            ptypes = getToolByName(self.context, 'portal_types')

            ec = self.view.export_context
            ec._profile_path = os.path.join(self.view.profile_location, 'types')
            
            if not os.path.exists(ec._profile_path):
                os.makedirs(ec._profile_path)
            exportObjects(ptypes[type_.id], '', ec)
        
    def generate(self):
        selected_types = []
        type_defs = ''
        for type_ in self.types:
            if 'export-' + type_.id in self.request:
                workflow_id = self.get_workflow_for(type_)
                selected_types.append((type_.id, workflow_id))
                self.generate_type(type_)
                type_defs += '\t<object name="%s" meta_type="Dexterity FTI"/>\n' % type_.id
                
        if not HAS_ZOPESKEL_DEXTERITY_INSTALLED:
            type_def_filename = os.path.join(self.view.profile_location,
                'types.xml')
            type_def = open(type_def_filename).read()
            fi = open(type_def_filename, 'w')
            fi.write(type_def.replace('<!-- -*- extra stuff goes here -*- -->', type_defs))
            fi.close()
                
        return selected_types
        
        
WORKFLOW_XML_TEMPLATE = \
"""<?xml version="1.0"?>
<object name="portal_workflow" meta_type="Plone Workflow Tool">
 <property name="title">Contains workflow definitions for your portal</property>
 %s
 <bindings>
  %s
 </bindings>
</object>
"""

class GenerateWorkflowApplication(BrowserView, BaseGenerator):
    
    template = ViewPageTemplateFile('templates/workflow-app-generator.pt')
    
    def __init__(self, context, request):
        super(GenerateWorkflowApplication, self).__init__(context, request)
        if self.dexterity_installed:
            self.type_generator = DexterityTypeGenerator(self)
        elif self.ploneformgen_installed:
            self.type_generator = PloneFormGenTypeGenerator(self)
        else:
            self.type_generator = None
            
        self.ps = getToolByName(self.context, 'portal_setup')
        self.export_context = DirectoryExportContext(self.ps, None)
        self.tmpdir = tempfile.mkdtemp()
    
    def add_workflows_for(self, selected_types):
        if len(selected_types) == 0:
            return

        workflow_xml_defs = ''
        workflow_xml_assignments = ''
        
        workflow_ids = set([t[1] for t in selected_types])
        
        for workflow_id in [id for id in workflow_ids if id not in plone_shipped_workflows]:
            workflow_xml_defs += '<object name="%s" meta_type="Workflow"/>\n' % workflow_id
            workflow = self.portal_workflow[workflow_id]
            profile_path = os.path.join(self.profile_location, 'workflows')
            self.export_context._profile_path = profile_path
            workflow_path = os.path.join(profile_path, workflow_id, 'scripts')
            os.makedirs(workflow_path)
            exportObjects(workflow, '', self.export_context)
        
        for type_id, workflow_id in selected_types:
            workflow_xml_assignments += \
"""
<type type_id="%s">
 <bound-workflow workflow_id="%s"/>
</type>
""" % (type_id, workflow_id)
        
        path = os.path.join(self.profile_location, 'workflows.xml')
        fi = open(path, 'w')
        fi.write(WORKFLOW_XML_TEMPLATE % (workflow_xml_defs, workflow_xml_assignments))
    
    @property
    def product_location(self):
        return os.path.join(self.tmpdir, self.dotted_namespace)
        
    @property
    def product_namespace_location(self):
        return os.path.join(self.product_location, self.namespace_package, 
            self.contained_namespace_package)
    
    @property
    def profile_location(self):
        return os.path.join(self.product_namespace_location, 'profiles', 'default')
    
    def write_file(self, path, body):
        fi = open(path, 'w')
        fi.write(body)
        fi.close()
    
    def add_content_rules(self):
        exporter = queryMultiAdapter((self.context, self.export_context), 
            IBody, name=u'plone.contentrules')
        if exporter is not None:
            body = exporter.body
            path = os.path.join(self.profile_location, 'contentrules.xml')
            if body is not None:
                self.write_file(path, body)
                
    def cleanup_package(self):
        # remove locales declaration from configure.zcml since there isn't
        # an actual locales directory
        configure_path = os.path.join(self.product_namespace_location, 
            'configure.zcml')
        content = open(configure_path).read()
        content = content.replace('<i18n:registerTranslations directory="locales" />', '')
        self.write_file(configure_path, content)
            
    def create_product(self):
        os.chdir(self.tmpdir)

        pm = getToolByName(self.context, 'portal_membership')
        member = pm.getAuthenticatedMember()

        command = DistroCommand('create')
        cmd = 'create -t %s %s --no-interactive' % (
            self.type_generator.create_command, self.dotted_namespace)
        args = cmd.split()
        command.run(args[1:], {
            'namespace_package': self.namespace_package, 
            'zope2product': True, 
            'description': '', 
            'author': member.getProperty('fullname', ''), 
            'author_email': member.getProperty('email', ''), 
            'license_name': 'GPL', 
            'package': self.contained_namespace_package, 
            'project': self.dotted_namespace, 
            'url': self.context.absolute_url(), 
            'version': self.request.get('package-version', '0.1'),
            'zip_safe': False, 
            'keywords': '', 
            'title': self.request.get('project-title', self.dotted_namespace), 
            'egg': self.dotted_namespace, 
            'long_description': ''
        })
        
        os.chdir(self.product_location)
            
    def generate(self):
        cwd = os.getcwd()
        self.create_product()
        selected_types = self.type_generator.generate()
        self.add_workflows_for(selected_types)
        self.cleanup_package()
        self.add_content_rules()
        os.chdir(cwd)
        tar_loc = os.path.join(self.tmpdir, '%s.tar' % self.dotted_namespace)
        path = os.path.join(self.tmpdir, self.dotted_namespace)
        tar = tarfile.TarFile(tar_loc, "w")
        tar.add(path, self.dotted_namespace)
        tar.close()
        self.request.response.setHeader('Content-Disposition', 'inline; filename=%s.tar' % self.dotted_namespace)
        self.request.response.setHeader('Content-Type', "application/x-tar")
        self.request.response.setHeader("Content-Length", os.path.getsize(tar_loc))
        return open(tar_loc).read()

    def can_use(self):
        return HAS_ZOPESKEL_INSTALLED and (self.ploneformgen_installed or self.dexterity_installed)
        
    def has_zopeskel_installed(self):
        return HAS_ZOPESKEL_INSTALLED

    def has_ploneformgen_installed(self):
        return self.ploneformgen_installed 

    def has_dexterity_installed(self):
        return self.dexterity_installed

        
    @property
    @memoize
    def qi(self):
        return getToolByName(self.context, 'portal_quickinstaller')
        
    @property
    @memoize
    def ploneformgen_installed(self):
        """
        Dexterity takes precidence over ploneformgen if installed
        """
        return not self.dexterity_installed and self.qi.isProductInstalled('PloneFormGen')
        
    @property
    @memoize
    def dexterity_installed(self):
        return self.qi.isProductInstalled('plone.app.dexterity')
    
    def __call__(self):
        utils = getToolByName(self.context, 'plone_utils')
        if not self.can_use:
            utils.addPortalMessage("""You must have ZopeSkel installed with 
PloneFormGen or Dexterity to use this tool. Please add ZopeSkel, PasteScript and Paste 
to the eggs section in your buildout and then install either PloneFormGen or Dexterity.""")
        else:
            if self.dexterity_installed and not HAS_ZOPESKEL_DEXTERITY_INSTALLED:
                utils.addPortalMessage("""If you install the zopeskel.dexterity
package, you'll be able to generate actual model and schema classes for Dexterity types.""")

        
        if self.can_use and self.request.get('form.submitted', False):
            return self.generate()
        else:
            return self.template()
            
        
    
