from optparse import OptionParser as BaseOptionParser, make_option
import glob
import os
import os.path
import qdj
import re
import sys


def get_template_root():
    return os.path.expanduser('~/.qdj')


def get_template_path(django_version):
    return os.path.join(get_template_root(), '%d.%d' % django_version[:2])


class OptionParser(BaseOptionParser):
    def __init__(self, **kwargs):
        subcommand = kwargs.pop('subcommand', None)
        if subcommand:
            prog = '%s %s' % (os.path.basename(sys.argv[0]), subcommand,)
            kwargs.setdefault('prog', prog)
        else:
            kwargs.setdefault('usage', '%prog subcommand')
        
        kwargs.setdefault('version', '%%prog %s' % (qdj.version_string(),))
        
        BaseOptionParser.__init__(self, **kwargs)
    
    def parse_args(self, args, values=None):
        return BaseOptionParser.parse_args(self, args, values)
    
    def too_many_arguments(self):
        self.error('Too many arguments')


def main():
    try:
        import django
    except ImportError:
        print 'Error: Django is not installed'
        exit(1)
    
    parser = OptionParser(option_list=(
        make_option('-d', '--debug', action='store_true', default=False),
    ))
    parser.disable_interspersed_args()
    options, args = parser.parse_args(sys.argv[1:])
    
    if len(args) < 1:
        parser.error('Expected subcommand')
    
    subcommand_name = args[0]
    subcommand = globals().get('subcommand_%s' % (subcommand_name,), None)
    
    if not subcommand:
        parser.error('Unknown subcommand "%s"' % (subcommand_name,))
    
    try:
        subcommand(args[1:])
    except BaseException, e:
        if options.debug or isinstance(e, (SystemExit, KeyboardInterrupt,)):
            raise
        else:
            print 'Error:', e


def subcommand_create(args):
    from qdj.projecttemplate import CreateProjectTemplate
    import django
    
    parser = OptionParser(subcommand='create')
    options, args = parser.parse_args(args)
    
    if len(args) != 0:
        parser.too_many_arguments()
    
    template_root = get_template_root()
    template_path = get_template_path(django.VERSION)
    
    if os.path.isdir(template_path):
        raise Exception('Template already exists in %s' % (template_path,))
    
    try:
        os.makedirs(template_root)
    except (IOError, OSError,), e:
        if not os.path.isdir(template_root):
            raise
    
    CreateProjectTemplate(template_path)
    
    print 'Created Django %d.%d template in %s' % (
        django.VERSION[0], django.VERSION[1], template_path,
    )


def subcommand_start(args):
    def confirm(prompt):
        while True:
            response = raw_input(prompt).lower()
            if response == 'y':
                return True
            elif response == 'n':
                return False
    
    from django.core.management import call_command
    from qdj.projecttemplate import UseProjectTemplate
    import django
    
    parser = OptionParser(subcommand='start', usage='%prog start project')
    options, args = parser.parse_args(args)
    
    if len(args) < 1:
        parser.error('Expected project name')
    elif len(args) > 1:
        parser.too_many_arguments()
    else:
        project_path = args[0]
    
    template_root = get_template_root()
    template_path = get_template_path(django.VERSION)
    
    if not os.path.isdir(template_path):
        if os.path.isdir(template_root):
            available_versions = tuple(
                tuple(map(int, os.path.basename(filename).split('.', 1)))
                for filename
                in glob.glob(os.path.join(template_root, '*'))
                if os.path.isdir(filename)
                and re.search(r'^\d+\.\d+$', os.path.basename(filename))
            )
        else:
            available_versions = ()
        
        if not available_versions:
            print 'There are no project templates. You can create a template with "qdj create"'
            if confirm('Would you like to use "django-admin.py startproject" instead? (y/n) '):
                project_path = os.path.abspath(project_path)
                project_dirname = os.path.dirname(project_path)
                project_basename = os.path.basename(project_path)
                os.chdir(project_dirname)
                call_command('startproject', project_basename)
                return
            else:
                print 'Aborted.'
                return
        else:
            use_version = sorted(available_versions)[-1]
            
            print 'You don\'t have any Django %d.%d templates.' % django.VERSION[:2]
            if confirm('Would you like to use your Django %d.%d template instead? (y/n) ' % use_version):
                template_path = get_template_path(use_version)
            else:
                print 'Aborted.'
                return
    
    UseProjectTemplate(template_path, project_path)


if __name__ == '__main__':
    main()
