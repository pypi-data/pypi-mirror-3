from optparse import OptionParser as BaseOptionParser, make_option
from qdj.projecttemplate import CreateProjectTemplate, UseProjectTemplate
import django
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
            raise Exception('There are no project templates. Create a template with "qdj create"')
        
        use_version = sorted(available_versions)[-1]
        
        print 'You don\'t have any Django %d.%d templates.' % django.VERSION[:2]
        prompt = 'Would you like to use your Django %d.%d template instead? (y/n) ' % use_version
        while True:
            response = raw_input(prompt).lower()
            if response == 'y':
                template_path = get_template_path(use_version)
                break
            elif response == 'n':
                print 'Aborted.'
                return
    
    UseProjectTemplate(template_path, project_path)


if __name__ == '__main__':
    main()
