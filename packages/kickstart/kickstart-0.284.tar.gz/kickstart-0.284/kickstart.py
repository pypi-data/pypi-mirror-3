#! /usr/bin/env python
import os, sys, shutil, re, yaml
from optparse import OptionParser
import kickstarter


parser = OptionParser()
parser.add_option("-t", "--template", dest="template", help="specify project template", default="default")
parser.add_option("-a", "--add-template", dest="new_template", help="add a new template directory") 
parser.add_option("-d", "--default-template", dest="default_template", help="set default template") 
(options, args) = parser.parse_args()


def create_template():
    if os.path.exists('./%s' % options.new_template):
        override = raw_input('%s already exists. Override? [y/n]: ' % options.new_template)

        if override == 'y':
            templates_dir = os.path.join(kickstarter.__path__[0], 'templates')
            shutil.rmtree('%s/%s' % (templates_dir, options.new_template))
            shutil.copytree(options.new_template, '%s/%s' % (templates_dir, os.path.dirname(options.new_template)))
        else:
            print 'Aborting'
    else:
        templates_dir = os.path.join(kickstarter.__path__[0], 'templates')
        shutil.copytree(options.new_template, '%s/%s' % (templates_dir, os.path.dirname(options.new_template)))


def set_default_template():
    templates_dir = os.path.join(kickstarter.__path__[0], 'templates')
    shutil.rmtree('%s/default' % templates_dir)
    shutil.copytree('%s/%s' % (templates_dir, options.default_template), '%s/%s' % (templates_dir, 'default'))
    shutil.copytree('%s/%s/%s' % (templates_dir, 'default', options.default_template), '%s/%s/%s' % (templates_dir, 'default', 'default')) 
    shutil.rmtree('%s/%s/%s' % (templates_dir, 'default', options.default_template))


def create_project():
    name = args[0]
    template_dir = os.path.join(kickstarter.__path__[0], 'templates', options.template)

    config = {}
    config['project_module'] = re.sub('\-', '_', args[0])
    config['project'] = re.sub('\-', '_', args[0])
    config['project_name'] = args[0]
    config['project_root'] = '%s/%s' % (os.getcwd(), args[0])

    def replace_variable(match):
        key = match.groups(1)[0].lower()
        return config[key]

    def config_prompt():
        if os.path.exists('%s/%s' % (template_dir, 'config.yaml')):
            c = open('%s/%s' % (template_dir, 'config.yaml'), 'r')
            parsed_conf = re.sub('{{\s*(\w+)\s*}}', args[0], c.read())
            c.close()

            conf = yaml.load(parsed_conf)
            for option in conf:
                default = conf[option]
                value = str(raw_input('%s (leave blank for %s): ' % (option, default)))
                config[option.lower()] = value if value != '' else default

    def copy_template():
        config_prompt()
        shutil.copytree(template_dir, name)
        shutil.copytree('%s/%s' % (name, options.template), '%s/%s' % (name, config['project_module'])) 
        shutil.rmtree('%s/%s' % (name, options.template))
        os.remove('%s/%s' % (name, 'config.yaml'))

        for dirname, dirnames, files in os.walk(name):
            for filename in files:
                f = open('%s/%s' % (dirname, filename), 'r')
                lines = f.readlines()
                f.close()

                first_pass = [re.sub('{{\s*(\w+)\s*}}', replace_variable, line) for line in lines]
                new_lines = [re.sub('__config_(\w+)__', replace_variable, line) for line in first_pass]

                f = open('%s/%s' % (dirname, filename), 'w')
                f.write(''.join(new_lines))
                f.close()

    if os.path.exists('./%s' % name):
        override = raw_input('%s already exists. Override? [y/n]: ' % name)

        if override == 'y':
            shutil.rmtree('./%s' % name)
            copy_template()
        else:
            print 'Aborting'
    else:
        copy_template()


if options.new_template:
    create_template()
elif options.default_template:
    set_default_template()
else:
    create_project()
