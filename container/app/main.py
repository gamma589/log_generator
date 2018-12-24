#!/usr/bin/env python3

import flashtext
import configparser
from faker import Faker
from datetime import datetime
import time
import random
import ast
import os
import logging
import logging.handlers


# How do we get the runtime parameters? 
# so far, we support 2 operational modes:
# environment based - for container deployments
# config based - standard and failsafe for the app
# in the works -> ESB runtime parameters if a use-case requirement appears

try:
    main_mode = os.environ['CONFIG_MODE']
    if main_mode == 'file':
        main_mode = 'fileConfig'
    elif main_mode == 'environment':
        main_mode = 'envConfig'
    else:
        main_mode = 'fileConfig'
except KeyError:
    main_mode = 'fileConfig'

fake = Faker()

def convert_ts(utc, format='%Y-%m-%d %H:%M:%S'):
    return str(datetime.utcfromtimestamp(utc).strftime(format))

def generate_log(template, lines, tstart):
    line_processor = flashtext.KeywordProcessor()
    if tstart == 'NOW':
        ts = 1284101485
    else:
        ts = tstart
    out_buff = ''
    with open(template) as f:
        templates = [x.strip() for x in f.readlines()]
    while lines > 0:
        length = len(templates)
        randu = random.randint(0, length-1)
        line = templates[randu]
        
        line_processor.add_keyword('%%PUB_IPV4%%', fake.ipv4())

        line_processor.add_keyword('%%PRIV_IPV4%%', fake.ipv4_private())

        line_processor.add_keyword('%%IPV6%%', fake.ipv6())

        line_processor.add_keyword('%%HOSTNAME%%', fake.hostname())

        line_processor.add_keyword('%%URI%%', fake.uri())

        line_processor.add_keyword('%%USER%%', fake.user_name())

        line_processor.add_keyword('%%EMAIL%%', fake.company_email())

        if tstart == 'NOW':
            line_processor.add_keyword('%%TS_1%%', convert_ts(time.time()))
            new_line = line_processor.replace_keywords(line)
        else:
            line_processor.add_keyword('%%TS_1%%', convert_ts(ts))
            new_line = line_processor.replace_keywords(line) + '\n'

        
        if tstart == 'NOW':
            pass
        else:
            ts = ts + random.randint(0,2)
        lines -= 1
        out_buff += new_line
    return out_buff

def main_conf():
    if config.has_section('output'):
        if (config.has_option('output', 'output_folder') and config.has_option('output', 'outputs')):
            log_config = ast.literal_eval(config.get('output','outputs'))
            log_folder = config.get('output', 'output_folder')
            for log in log_config:
                template = log['template']
                out_file = log['out_file']
                initial_ts = log['tstart']
                lines = log['lines']
                out_buf = generate_log(template=template, lines=lines, tstart=initial_ts)
                open(log_folder+'/'+out_file, 'w').write(out_buf)

def main_env():
    try:
        template = os.environ['TEMPLATE_NAME']
    except KeyError:
        print('Template name not found in environment, aborting!')
        quit()
    
    try:
        syslog_server = os.environ['SYSLOG_TARGET']
    except KeyError:
        print('Syslog destination not found, aborting')
        quit()
    
    syslogger = logging.getLogger('SyslogLogger')
    syslogger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address=(syslog_server, 514),
                                             facility=19)
    syslogger.addHandler(handler)
    out_file='log.log'
    while True:
        innerTemplate = '/log_generator/templates/'+template+'.template'
        line = generate_log(template=innerTemplate, lines=1, tstart='NOW')
        print(line)
        syslogger.log(msg=line, level=logging.INFO)
        open('/opt/logs/'+template+'/'+out_file, 'a').write(line)

def main():
    if main_mode == 'fileConfig':
        main_conf()
    elif main_mode == 'envConfig':
        main_env()
    else:
        pass

if __name__ == '__main__':
    main()