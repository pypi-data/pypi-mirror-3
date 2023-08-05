from optparse import OptionParser as BaseOptionParser, IndentedHelpFormatter as BaseHelpFormatter, make_option, SUPPRESS_HELP
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
            args.insert(0, '-h')
    
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
    
    parser = OptionParser(command='create')
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


def command_start(args):
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
    
    parser = OptionParser(command='start', usage='%prog project')
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
