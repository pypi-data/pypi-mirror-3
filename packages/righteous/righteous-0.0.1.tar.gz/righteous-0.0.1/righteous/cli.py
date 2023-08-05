#!/usr/bin/env python2.6
# coding: utf-8

import os
from datetime import datetime
from optparse import OptionParser, TitledHelpFormatter
from pprint import pprint
try:
    import json as simplejson
except ImportError:
    import simplejson

import righteous
from righteous.config import settings

from clint import resources
from clint.textui import colored


resources.init('Righteous', 'righteous')

# ['deployment_href', 'instance_type', 'ec2_security_groups_href', 'cloud_id', 'ec2_ssh_key_href', 'ec2_availability_zone', 'server_template_href']
server_defaults_file = 'server_defaults.json'
# ['username', 'password', 'default_deployment_id', 'account_id']
account_defaults_file = 'account_defaults.json'

def server_owner(server_info):
    owner = None
    for p in server_info['parameters']:
        if p['name']=='EMAIL':
            owner = p['value'][5:]
    return owner

def print_running_servers(servers, exclude_states=['stopped']):
    now = datetime.now()
    output = []

    for server in servers['servers']:
        server_info = righteous.server_info(server['href'])
        server_settings = righteous.server_settings(server['href'])
        owner = server_owner(server_info)
        running = now - datetime.strptime(server['created_at'], '%Y/%m/%d %H:%M:%S +0000')
        if server['state'] not in exclude_states:
            output.append(dict(days=running.days, output='[%s] %s (%s) by %s running for %s days' % (server['state'],
                '%s @ %s' % (server['nickname'], server_settings['dns-name'] if 'dns-name' in server_settings else 'unknown'),
                server_settings['ec2-instance-type'], owner, running.days)))
    output.sort()
    output.reverse()

    for o in output:
        print(o['output'])

# def delete_stopped_servers(servers):
#     for server in servers['servers']:
#         if server['state']=='stopped':
#             righteous.delete_server(server['href'])

# def stop_stranded_servers(servers):
#     for server in servers['servers']:
#         if server['state']=='stranded':
#             righteous.stop_server(server['href'])

# http://stackoverflow.com/questions/392041/python-optparse-list
def comma_split(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def read_defaults(account_path=None, server_path=None):
    server_defaults = simplejson.loads(resources.user.read(server_path) if server_path else open(server_defaults_file).read())
    account_defaults = simplejson.loads(resources.user.read(account_path) if account_path else open(account_defaults_file).read())
    return account_defaults, server_defaults

def write_defaults(account_defaults, server_defaults):
    resources.user.write(account_defaults_file, simplejson.dumps(account_defaults))
    resources.user.write(server_defaults_file, simplejson.dumps(server_defaults))

# FIXME: this all needs to move to a configuration file that is required on first use
# and then saved to the AUTH_FILE
server_template_map = {
    'm1.small':'https://my.rightscale.com/api/acct/281/ec2_server_templates/52271',
    'm1.large':'https://my.rightscale.com/api/acct/281/ec2_server_templates/122880',
}
# defaults = dict(ec2_security_groups_href = 'https://my.rightscale.com/api/acct/281/ec2_security_groups/540',
#                 ec2_availability_zone = 'us-east-1a',
#                 ec2_ssh_key_href = 'https://my.rightscale.com/api/acct/281/ec2_ssh_keys/758',
#                 cloud_id='1',
#                 server_template_href = 'https://my.rightscale.com/api/acct/281/ec2_server_templates/52271',
#                 instance_type = 'm1.small',
#                 deployment_href='https://my.rightscale.com/api/acct/281/deployments/38823',)
# account_defaults = dict(username = 'foo',
#                         password = 'bar',
#                         default_deployment_id = '38823',
#                         account_id = '281')

if __name__ == '__main__':
    parser = OptionParser(formatter=TitledHelpFormatter(width=78))
    parser.add_option('-l', '--list', dest='list_servers', action='store_true', help='List running integration environments')
    parser.add_option('-k', '--kill', dest='kill_env', type='string', help='Stops a comma-separated list of integration environments', action='callback', callback=comma_split)
    parser.add_option('-s', '--status', dest='server_status', type='string', help='Lists the status of a comma-separated list of integration environments', action='callback', callback=comma_split)
    parser.add_option('-r', '--remove', dest='delete_env', type='string', help='Deletes a comma-separated list of integration environments', action='callback', callback=comma_split)
    parser.add_option('-c', '--create', dest='envname', type='string', help='Create an integration environment')
    parser.add_option('-b', '--branches', dest='branches', type='string', help='Branches to build')
    parser.add_option('-e', '--email', dest='email', type='string')
    parser.add_option('-i', '--instance-type', dest='instance_type', type='string', help='Specify the instance size (small/large)')

    parser.add_option('--account-defaults-path', dest='account_defaults_path', type='string', help='Path to the accounts defaults json file, will be saved in %s for future use.' % account_defaults_file)
    parser.add_option('--server-defaults-path', dest='server_defaults_path', type='string', help='Path to the server defaults json file, will be saved in %s for future use.' % server_defaults_file)

    # parser.add_option('-u', '--username', dest='username', type='string')
    # parser.add_option('-p', '--password', dest='password', type='string')
    # parser.add_option('-a', '--account_id', dest='account_id', type='string')
    parser.add_option('-d', '--debug', dest='debug', action='store_true')

    (options, args) = parser.parse_args()

    # if no defaults file supplied on the command line, look for it in account defaults

    account_defaults, server_defaults = read_defaults(options.account_defaults_path, options.server_defaults_path)
    righteous.init(account_defaults, server_defaults, debug=options.debug)
    if righteous.login():
        write_defaults(account_defaults, server_defaults)
    else:
        print(colored.red('Authentication failed'))
        exit(2)

    # TODO: cli preamble
    if options.list_servers:
        servers = righteous.list_deployment_servers()
        print_running_servers(servers, exclude_states=[])

    elif options.envname and options.email:
        if options.instance_type and options.instance_type in ['small','large']:
            settings.server_defaults['instance_type'] = 'm1.%s' % options.instance_type
            settings.server_defaults['server_template_href'] = server_template_map[server_defaults['instance_type']]

        parameters = dict(envname=options.envname, email=options.email, mode='unattended', branches=options.branches if options.branches else 'none')

        successful, location = righteous.create_and_start_server(options.envname, parameters)
        if successful:
            print(colored.cyan('Created and started environment %s @ %s' % (options.envname, location)))
        else:
            print(colored.red('Failed to create environment %s' % options.envname))

    elif options.kill_env:
        for env in options.kill_env:
            answer = raw_input(colored.cyan('Confirm deletion of %s ([enter/y]/[n|no]) ' % env))
            if answer in ['n', 'no']:
                continue
            # server = righteous.find_server(env)
            # successful = righteous.stop_server(server['href'])
            successful = righteous.stop_server(env)
            if successful:
                print(colored.yellow('Initiated decommissioning %s' % env))

    elif options.server_status:
        for env in options.server_status:
            server = righteous.find_server(env)
            server_settings = righteous.server_settings(server['href'])
            if server and options.debug:
                server_info = righteous.server_info(server['href'])
                if options.debug:
                    pprint(server_info)
                    pprint(server_settings)
            # TODO: colour output by server state
            # color = colored.cy
            # if server['state'] == '
            print(colored.cyan('%s (%s): %s' % (env, server_settings['ec2-instance-type'], '%s %s' % (server['href'], server['state']) if server else 'Not Found')))

    elif options.delete_env:
        for env in options.delete_env:
            # server = righteous.find_server(env)
            # successful = righteous.delete_server(server['href'])
            successful = righteous.delete_server(env)
            if successful:
                print(colored.cyan('Successfully deleted %s @ %s' % (env, server['href'])))
    else:
        parser.print_help()

