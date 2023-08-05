from optparse import OptionParser as BaseOptionParser
from optparse import IndentedHelpFormatter as BaseHelpFormatter
from optparse import make_option, SUPPRESS_HELP
import os
import os.path
import qdj
import re
import sys


DEFAULT_TEMPLATE_NAME = 'default'
VERSION_RE = re.compile(r'^(\d+)\.(\d+)$')


def main():
    try:
        import django
    except ImportError:
        print 'Error: Django is not installed'
        exit(1)
    
    parser = OptionParser(
        description='QDJ is like "django-admin.py startproject", but with your own project templates.',
        option_list=(
            make_option('-d', '--debug', action='store_true', default=False, help=SUPPRESS_HELP),
        ),
        epilog=(
            'Available commands:\n'
            '    create   Create a project template for the active Django version\n'
            '    start    Start a project from a template\n'
            '\n'
            'Type \'qdj help COMMAND\' for more information on a specific command.'
        ),
    )
    parser.disable_interspersed_args()
    options, args = parser.parse_args(sys.argv[1:])
    
    if len(args) < 1:
        parser.print_help()
        exit(1)
    
    command_name = args.pop(0)
    
    if command_name == 'help':
        if len(args) == 0:
            parser.print_help()
            return
        else:
            command_name = args.pop(0)
            args = ['--help'] + args
    
    command = globals().get('command_%s' % (command_name,), None)
    
    if not command:
        parser.error('Unknown command "%s"' % (command_name,))
    
    try:
        command(args)
    except BaseException, e:
        if options.debug or isinstance(e, (SystemExit, KeyboardInterrupt,)):
            raise
        else:
            print 'Error:', e


def command_create(args):
    from qdj.projecttemplate import CreateProjectTemplate
    import django
    
    parser = OptionParser(command='create', usage='%prog [TEMPLATENAME]')
    options, args = parser.parse_args(args)
    
    if len(args) > 1:
        parser.too_many_arguments()
    elif len(args) == 1:
        template_name = args[0]
    else:
        template_name = DEFAULT_TEMPLATE_NAME
    
    template_path = get_template_path(template_name)
    template_version_path = get_template_version_path(template_name, django.VERSION)
    
    if os.path.isdir(template_version_path):
        raise Exception('Template already exists in %s' % (template_version_path,))
    
    try:
        os.makedirs(template_path)
    except (IOError, OSError,), e:
        if not os.path.isdir(template_path):
            raise
    
    CreateProjectTemplate(template_version_path)
    
    print 'Created Django %d.%d template in %s' % (
        django.VERSION[0], django.VERSION[1], template_version_path,
    )


def command_start(args):
    from django.core.management import call_command
    from qdj.projecttemplate import UseProjectTemplate, create_django_project
    import django
    
    parser = OptionParser(command='start', usage='%prog [TEMPLATENAME] PROJECT')
    options, args = parser.parse_args(args)
    
    if len(args) < 1:
        parser.error('Expected project name')
    elif len(args) > 2:
        parser.too_many_arguments()
    elif len(args) == 2:
        template_name, project_path = args
    else:
        template_name, project_path = DEFAULT_TEMPLATE_NAME, args[0]
    
    template_version = django.VERSION[:2]
    
    if not os.path.isdir(get_template_version_path(template_name, template_version)):
        available_versions = list(get_template_versions(template_name))
        
        usable_versions = list(
            version
            for version in available_versions
            if version < django.VERSION
        )
        
        if usable_versions:
            template_version = sorted(available_versions)[-1]
            print 'There are no "%s" templates for Django %d.%d' % (
                template_name, django.VERSION[0], django.VERSION[1],
            )
            print
            if not confirm('Would you like to use your Django %d.%d template instead? (y/n) ' % template_version):
                print 'Aborted.'
                return
        
        if not usable_versions:
            if available_versions:
                print 'There are no suitable "%s" templates for Django %d.%d' % (
                    template_name, django.VERSION[0], django.VERSION[1],
                )
            else:
                print 'There are no templates named "%s".' % (template_name,)
            
            print 'You can create one with "qdj create %s"' % (template_name,)
            print
            
            if confirm('Would you like to use "django-admin.py startproject" instead? (y/n) '):
                create_django_project(project_path)
                return
            else:
                print 'Aborted.'
                return
    
    UseProjectTemplate(
        get_template_version_path(template_name, template_version),
        project_path,
    )


def get_template_root():
    return os.path.expanduser('~/.qdj')


def get_template_path(template_name):
    return os.path.join(get_template_root(), template_name)


def get_template_version_path(template_name, django_version):
    return os.path.join(get_template_path(template_name), '%d.%d' % django_version[:2])


def get_template_versions(template_name):
    template_path = get_template_path(template_name)
    try:
        for filename in os.listdir(template_path):
            if not os.path.isdir(os.path.join(template_path, filename)):
                continue
            
            match = VERSION_RE.search(filename)
            if not match:
                continue
            
            yield (int(match.group(1)), int(match.group(2)),)
    except (IOError, OSError,):
        if os.path.isdir(template_path):
            raise


def confirm(prompt):
    while True:
        response = raw_input(prompt).lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False


class OptionParser(BaseOptionParser):
    def __init__(self, **kwargs):
        command = kwargs.pop('command', None)
        if command:
            prog = '%s %s' % (os.path.basename(sys.argv[0]), command,)
            kwargs.setdefault('prog', prog)
        else:
            kwargs.setdefault('usage', '%prog COMMAND')
        
        kwargs.setdefault('version', '%%prog %s' % (qdj.version_string(),))
        kwargs.setdefault('formatter', HelpFormatter())
        
        BaseOptionParser.__init__(self, **kwargs)
    
    def parse_args(self, args, values=None):
        return BaseOptionParser.parse_args(self, args, values)
    
    def too_many_arguments(self):
        self.error('Too many arguments')


class HelpFormatter(BaseHelpFormatter):
    def format_epilog(self, epilog):
        if epilog:
            # Preserve linebreaks in epilog
            return '\n' + ('\n'.join(
                self._format_text(paragraph)
                for paragraph
                in str(epilog).split('\n')
            )) + '\n'
        else:
            return ''    


if __name__ == '__main__':
    main()
