#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import datetime
import stat
import random
import struct
import configparser
from jinja2 import Environment, FileSystemLoader, StrictUndefined

DEFAULT_TEMPLATES_DIR = os.getcwd()
def read_config(cfg_f, cpu, datasymmode, peripheralmodel, cachefilename, rulefilename, firmwarename, debug, testcasename):
    if not os.path.isfile(cfg_f):
        sys.exit("Cannot find the specified configuration file: %s" % cfg_f)
    parser = configparser.ConfigParser()
    parser.read(cfg_f)

    # Prepare the target firmware lua configuration
    config = {
        'loglevel': "debug" if debug else "info",
        'creation_time': str(datetime.datetime.now()),
        'firmware_name': firmwarename,
        'pwd': str(os.getcwd()),
        # Configure the uEmu is in fuzzing(true) phase or KB(false) extraction phase
        'peripheral_model_name': peripheralmodel,
		'datasymmode': "true" if datasymmode else "false",
		'klee_info': "false" if datasymmode else "true",
		'cpu_arch': cpu
    }

    # MEM
    config['rom'] = parser.get("MEM_Config","rom").split( )
    config['ram'] = parser.get("MEM_Config","ram").split( )
    config['vtor'] = int(parser.get("MEM_Config","vtor"), 16)

    # IRQ
    config['irq_tb_break'] = parser.getint("IRQ_Config","irq_tb_break")
    config['disable_irqs'] = parser.get("IRQ_Config","disable_irqs").split()
    config['disable_systick'] = parser.get("IRQ_Config","disable_systick")
    if config['disable_systick'] == "true":
        config['systick_begin_point'] = parser.get("IRQ_Config","systick_begin_point")

    # Invlid states detection
    config['bb_inv1'] = parser.getint("INV_Config","bb_inv1")
    config['bb_inv2'] = parser.getint("INV_Config","bb_inv2")
    config['bb_terminate'] = parser.getint("INV_Config","bb_terminate")
    config['kill_points'] = parser.get("INV_Config","kill_points").split()
    config['alive_points'] = parser.get("INV_Config","alive_points").split()

    if peripheralmodel == "uEmu":
        config['cache_file_name'] = cachefilename if datasymmode else ""
        # TC
        config['t2_function_parameter_num'] = parser.getint("TC_Config","t2_function_parameter_num")
        config['t2_caller_level'] = parser.getint("TC_Config","t2_caller_level")
        config['t2_max_context'] = parser.getint("TC_Config","t2_max_context")
        config['t3_max_symbolic_count'] = parser.getint("TC_Config","t3_max_symbolic_count")
    else: # NLP Peripheral Model
        config['nlp_file_name'] = nlpfilename   

    # Testcase
    config['enable_tc'] = "true" if testcasename else "false"
    if config['enable_tc'] == "true":
        config['testcase_name'] = testcasename

    return config

def _init_template_env(templates_dir=None):
    """
    Initialize the jinja2 templating environment using the templates in the
    given directory.
    """
    if not templates_dir:
        templates_dir = DEFAULT_TEMPLATES_DIR

    env = Environment(loader=FileSystemLoader(templates_dir),
                      autoescape=False, undefined=StrictUndefined)

    return env

def render_template(context, template, output_path, templates_dir=None,
                    executable=False):
    """
    Renders the ``template`` template with the given ``context``. The result is
    returned as a string and written to ``output_path`` (if specified).
    A directory containing the Jinja templates can optionally be specified.
    """
    env = _init_template_env(templates_dir)

    rendered_data = env.get_template(template).render(context)

    # Remove trailing spaces
    cleaned_lines = []
    for line in rendered_data.splitlines():
        cleaned_lines.append(line.rstrip())
    rendered_data = '\n'.join(cleaned_lines)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(rendered_data)

        if executable:
            st = os.stat(output_path)
            os.chmod(output_path, st.st_mode | stat.S_IEXEC)

    return rendered_data

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("cpu", type=str, default="ARMv7m",
                            help="Configure the CPU arch of target firmware. e.g., ARMv7m (default), ARMv6m")
    parser.add_argument("firmware", type=str,
                            help="Configure the firmware name will run on SymEmu")
    parser.add_argument("config", type=str, default="",
                            help="Configure the configuration file used for Knowledge Base extration. e.g., SymEmu.cfg")
    parser.add_argument("--debug", action="store_true",
                            help="In debug datasymmode, uEmu will output huge log, please ensure you have enough space (e.g., more than 100M)")	
    parser.add_argument("-kb", "--KBfilename", type=str, default="",
                            help="Configure the Knownledge Base filename used for uEmu peripheral model")
    parser.add_argument("-rule", "--rulefilename", type=str, default="",
                            help="Configure the C-A Rule filename used for SEmu peripheral model")
    parser.add_argument("-t", "--testcasefilename", type=str, default="",
                            help="Configure the testcase filename used for dynamic analysis")

    args = parser.parse_args()

    if args.config != "":
        args.config = os.path.abspath(args.config)
    else:
        sys.exit("Please set configuration .cfg file!")
    if args.testcasefilename == "":
        print("No testcasefile given.")
    else:
        print("uEmu or SEmu will use %s file as input for dynamic analysis and will automatically exit when whole testcase has been consumed." % (args.testcasefilename));
    if args.KBfilename == "":
        if args.rulefilename == "":
            peripheralmodel = "uEmu"
            if args.debug:
                print("%s firmware has been configured using uEmu in knowledge extraction phase with debug level log, now you can use launch-SymEmu.sh script to run it." % (args.firmware))
            else:
                print("%s firmware has been configured using uEmu in knowledge extraction phase with info level log, now you can use launch-SymEmu.sh script to run it." % (args.firmware))
            datasymmode = False
        else:
            datasymmode = True
            peripheralmodel = "SEmu"
            if args.debug:
                print("%s firmware has been configured using SEmu with debug level log" % (args.firmware))
            else:
                print("%s firmware has been configured using SEmu with warning level log" % (args.firmware))
    else:
        datasymmode = True
        peripheralmodel = "uEmu"
        if args.debug:
            print("%s firmware has been configured using uEmu in dynamic analysis phase with debug level log, now you can use launch-SymEmu.sh script to run it." % (args.firmware))
        else:
            print("%s firmware has been configured using uEmu in dynamic analysis phase with info level log, now you can use launch-SymEmu.sh script to run it." % (args.firmware))
    config = read_config(args.config, args.cpu, datasymmode, peripheralmodel, args.KBfilename, args.rulefilename, args.firmware, args.debug, args.testcasefilename)
    render_template(config, "SymEmu-config-template.lua", "SymEmu-config.lua")    
    launch = {
        'creation_time': str(datetime.datetime.now()),
        'qemu_arch':"arm",
        'memory':"2M",
        'firmware': args.firmware,
        'root_dir': os.environ['SymEmuDIR'],
    }
    render_template(launch, "launch-SymEmu-template.sh", "launch-SymEmu.sh", executable=True)


if __name__ == "__main__":
    # sys.argv[1:]为要处理的参数列表，sys.argv[0]为脚本名，所以用sys.argv[1:]过滤掉脚本名
    main(sys.argv[1:])
