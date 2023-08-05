"""
Create and use templates for Django projects.
"""


from django.core.management import call_command
import django
import imp
import jinja2
import os
import random
import re
import shutil
import string
import sys
import tempfile


def random_token(length, chrs, random=random.SystemRandom()):
    return ''.join(random.choice(chrs) for i in xrange(length))


class CreateProjectTemplate(object):
    """
    Create a project template using the active version of Django.
    
    Replaces the project name and secret key with placeholders, for later
    interpretation by Jinja2.
    """
    
    def __init__(self, template_path):
        self.template_path = os.path.abspath(template_path)
        
        self.temp_project_basename = '_%s' % random_token(16, string.ascii_lowercase)
        self.temp_project_dirname = tempfile.gettempdir()
        self.temp_project_path = os.path.join(
            self.temp_project_dirname,
            self.temp_project_basename,
        )
        
        os.mkdir(self.template_path)
        
        prev_cwd = os.getcwd()
        try:
            os.chdir(self.temp_project_dirname)
            try:
                call_command('startproject', self.temp_project_basename)
                shutil.copytree(self.temp_project_path, os.path.join(self.template_path, 'files'))
                self.modify_files()
            finally:
                shutil.rmtree(self.temp_project_path)
        finally:
            os.chdir(prev_cwd)
    
    def modify_files(self):
        for path, dirnames, filenames in os.walk(self.template_path):
            for filename in filenames:
                filename = os.path.join(path, filename)
                source = open(filename, 'rb').read()
                source = self.modify_file(source)
                open(filename, 'wb').write(source)
    
    def modify_file(self, source):
        source = self.replace_project_name(source)
        source = self.replace_secret_key(source)
        return source
    
    def replace_project_name(self, source):
        return source.replace(self.temp_project_basename, '{{ project_name }}')
    
    def replace_secret_key(self, source):
        return re.sub(
            r"(?m)^SECRET_KEY = '[^']*'",
            "SECRET_KEY = '{{ random_secret_key() }}'",
            source,
        )


class UseProjectTemplate(object):
    """
    Use a project template as built by CreateProjectTemplate.
    """
    
    template_exts = ('.py', '.txt',)
    
    def __init__(self, template_path, project_path, template_exts=None):
        self.template_path = os.path.abspath(template_path)
        self.project_path = project_path
        if template_exts is not None:
            self.template_exts = template_exts
        
        self.project_basename = os.path.basename(self.project_path)
        
        self.env = jinja2.Environment(autoescape=False)
        self.setup_jinja2_env()
        
        # Try to load the hooks module before doing anything, so that import errors
        # can be diagnosed.
        self.get_hooks_module()
        
        shutil.copytree(os.path.join(self.template_path, 'files'), self.project_path)
        self.modify_files()
        self.post_create()
    
    def setup_jinja2_env(self):
        self.env.globals.update(
            django_version=django.get_version(),
            project_name=self.project_basename,
            random_secret_key=self.random_secret_key,
        )
    
    def modify_files(self):
        for path, dirnames, filenames in os.walk(self.project_path):
            for filename in filenames:
                if not filename.endswith(self.template_exts):
                    continue
                
                filename = os.path.join(path, filename)
                source = self.modify_file(open(filename).read())
                open(filename, 'w').write(source)
    
    def modify_file(self, source):
        return self.env.from_string(source).render()
    
    def post_create(self):
        hook = self.get_hook('post_create')
        if not hook:
            return
        
        prev_dir = os.getcwd()
        prev_sys_path = sys.path
        try:
            os.chdir(self.project_path)
            sys.path = [
                self.project_path,
                os.path.join(self.project_path, '..'),
            ] + sys.path
            os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % (self.project_basename,)
            
            hook()
        finally:
            os.chdir(prev_dir)
            sys.path = prev_sys_path
    
    def get_hook(self, name):
        hooks_module = self.get_hooks_module()
        if not hooks_module:
            return
        if not hasattr(hooks_module, name):
            return
        return getattr(hooks_module, name)
    
    def get_hooks_module(self):
        if not hasattr(self, '_hooks'):
            hooks_filename = os.path.join(self.template_path, 'hooks.py')
            try:
                self._hooks = imp.load_module(
                    'hooks', open(hooks_filename), hooks_filename,
                    ('.py', 'r', imp.PY_SOURCE),
                )
            except (IOError,):
                if os.path.isfile(hooks_filename):
                    raise
                else:
                    self._hooks = None
        return self._hooks
    
    def random_secret_key(self):
        return random_token(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
