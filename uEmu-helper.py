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
def read_config(cfg_f, mode, cachefilename, firmwarename, debug):
    if not os.path.isfile(cfg_f):
        sys.exit("Cannot find the specified configuration file: %s" % cfg_f)
    parser = configparser.SafeConfigParser()
    parser.read(cfg_f)

    # Prepare the target firmware lua configuration
    config = {
        'loglevel': "debug" if debug else "info",
        'creation_time': str(datetime.datetime.now()),
        'firmware_name': firmwarename,
        'pwd': str(os.getcwd()),
        # Configure the uEmu is in fuzzing(true) phase or KB(false) extraction phase
        'mode': "true" if mode else "false",
		'klee_info': "false" if mode else "true",
        # If using fuzzing phase, the KB file name should be configured
        'cache_file_name': cachefilename if mode else "",
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

    # TC
    config['t2_function_parameter_num'] = parser.getint("TC_Config","t2_function_parameter_num")
    config['t2_caller_level'] = parser.getint("TC_Config","t2_caller_level")
    config['t2_max_context'] = parser.getint("TC_Config","t2_max_context")
    config['t3_max_symbolic_count'] = parser.getint("TC_Config","t3_max_symbolic_count")

    # Fuzzing target
    if config['mode'] == "true":
        config['enable_fuzz'] = parser.get("Fuzzer_Config","enable_fuzz")
        config['allow_auto_mode_switch'] = parser.get("Fuzzer_Config","allow_auto_mode_switch")
    else:
        config['enable_fuzz'] = "false"
    if config['enable_fuzz'] == "true":
        config['additional_writable_ranges'] = parser.get("Fuzzer_Config","additional_writable_ranges").split( )
        config['input_peripherals'] = parser.get("Fuzzer_Config","input_peripherals").split( )
        config['time_out'] = parser.getint("Fuzzer_Config","time_out")
        config['crash_points'] = parser.get("Fuzzer_Config","crash_points").split()
        config['allow_new_phs'] = parser.get("Fuzzer_Config","allow_new_phs")
        config['fork_count'] = parser.get("Fuzzer_Config","fork_count")

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
    parser.add_argument("firmware", type=str,
                            help="Configure the firmware name will run on uEmu")
    parser.add_argument("config", type=str, default="",
                            help="Configure the configuration file used for Knowledge Base extration. e.g., uEmu.cfg")
    parser.add_argument("--debug", action="store_true",
                            help="In debug mode, uEmu will output huge log, please ensure you have enough space (e.g., more than 100M)")	
    parser.add_argument("-kb", "--KBfilename", type=str, default="",
                            help="Configure the Knownledge Base filename used for uEmu")
    parser.add_argument("-s", "--seedfilename", type=str, default="",
                            help="Configure the fuzzing seed filename used for AFL fuzzer")

    args = parser.parse_args()

    if args.config != "":
        args.config = os.path.abspath(args.config)
    else:
        sys.exit("Please set configuration .cfg file!")

    if args.KBfilename == "":
        if args.debug:
            print("%s firmware has been configured using uEmu in knowledge extraction phase with debug level log, now you can use launch-uEmu.sh script to run it." % (args.firmware))
        else:
            print("%s firmware has been configured using uEmu in knowledge extraction phase with info level log, now you can use launch-uEmu.sh script to run it." % (args.firmware))
        mode = False
    else:
        if args.seedfilename == "":
            list_random = []
            for num in range(0,4):
                randomseed = random.randint(0,127)
                list_random.append(randomseed)
            with open('testcase', 'wb') as f:
                for r in list_random:
                    rd = struct.pack('B', r)
                    f.write(rd)
            seedfilename = 'testcase'
            print("Random initial seed %d %d %d %d will be used in dynamic analysis (fuzzing) phase." % (list_random[0], list_random[1], list_random[2], list_random[3]))
        else:
            seedfilename = args.seedfilename
            print("uEmu will use manual seed file %s in dynamic analysis (fuzzing) phase." % (args.seedfilename))
        afl = {
            'creation_time': str(datetime.datetime.now()),
            'firmware': args.firmware,
            'seed': seedfilename,
        }
        render_template(afl, "launch-AFL-template.sh", "launch-AFL.sh", executable=True)
        if args.debug:
            print("%s firmware has been configured using uEmu in dynamic analysis (fuzzing) phase with debug level log." % (args.firmware))
        else:
            print("%s firmware has been configured using uEmu in dynamic analysis (fuzzing) phase with info level log." % (args.firmware))
        mode = True
        print("Next please first run launch-AFL.sh in one shell and use another shell to run launch-uEmu.sh.")
    config = read_config(args.config, mode, args.KBfilename, args.firmware, args.debug)
    render_template(config, "uEmu-config-template.lua", "uEmu-config.lua")
    launch = {
        'creation_time': str(datetime.datetime.now()),
        'qemu_arch':"arm",
        'memory':"2M",
        'firmware': args.firmware,
        'root_dir': os.environ['uEmuDIR'],
    }
    render_template(launch, "launch-uEmu-template.sh", "launch-uEmu.sh", executable=True)


if __name__ == "__main__":
    # sys.argv[1:]为要处理的参数列表，sys.argv[0]为脚本名，所以用sys.argv[1:]过滤掉脚本名
    main(sys.argv[1:])
