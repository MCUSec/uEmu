# μEmu

A Universal MCU Firmware Emulator for Dynamic Analysis without Any Hardware Dependence

## General Idea

Unlike existing MCU firmware dynamic analysis tools that forwards the interactions with unsupported peripherals to the real hardware, μEmu takes the firmware image as input and symbolically executes it by representing unknown peripheral registers as symbols.
During symbolic execution, it infers the rules to respond to unknown peripheral accesses. These rules are stored in a knowledge base (KB), which is referred to firmware during dynamic analysis **without any hardware dependence**. The detail of μEmu design and implementation, please refer to our paper.

## Citing our paper

```bibtex
@inproceedings {uEmu,
author = {Wei Zhou and Le Guan and Peng Liu and Yuqing Zhang},
title = {Automatic Firmware Emulation through Invalidity-guided Knowledge Inference},
booktitle = {30th {USENIX} Security Symposium ({USENIX} Security 21)},
year = {2021},
url = {https://www.usenix.org/conference/usenixsecurity21/presentation/zhou},
publisher = {{USENIX} Association},
}
```


## Directory structure of the repo

```
.
├── LICENSE
├── README.md
├── docs                     # more documentation about implementation and configuration
├── SymEmu-helper.py           # helper scripts to configurate μEmu based on configration file (e.g., μEmu.cfg)
├── launch-SymEmu-template.sh  # template scripts to launch μEmu
├── SymEmu-config-template.lua # template config file of μEmu and S2E plugins
├── library.lua              # contains convenience functions for the SymEmu-config.lua file.
├── ptracearm.h
├── totalbbrange.py          # IDA plugin for basic block range calculation
├── vagrant-bootstrap.sh     # bootstrap file for vagrant box
└── Vagrantfile              # configuration file for vagrant box
```

## Source Code Installation

**Note**:
1. SymEmu builds and runs on Ubuntu 18.04 and above (64-bit). Earlier versions may still work, but we do not support them anymore.

2. Since the qemu in arm kvm mode will use ptrace.h which is from the host arm linux kernel, however the real host μEmu is X86, so you have to add ptracearm.h from [linux source code](https://elixir.bootlin.com/linux/latest/source/arch/arm/include/asm/ptrace.h) (you can directly download it from this repo) to the your local path: ``/usr/include/x86_64-linux-gnu/asm``.

### Required packages

You must install a few packages in order to build μEmu manually.
The required packages of μEmu is same as the current S2E 2.0,
You can check out all [required packages](https://github.com/MCUSec/uEmu/blob/main/vagrant-bootstrap.sh#L8) from line 8 to 21 in the Vagrant script.


### Checking out source code

The μEmu source code can be obtained from the my git repository using the following commands.

```console
 export SymEmuDIR=/home/user/SymEmu  # SymEmuDIR must be in your home folder (e.g., /home/user/SymEmu)
 sudo apt-get install git-repo   # or follow instructions at https://gerrit.googlesource.com/git-repo/
 cd $SymEmuDIR
 repo init -u https://github.com/MCUSec/manifest.git -b Pipe
 repo sync
```
This will set up the μEmu repositories in ``$SymEmuDIR``.


### Building μEmu

The μEmu Makefile can be run as follows:

```console
    $ sudo mkdir $SymEmuDIR/build
    $ cd $SymEmuDIR/build
    $ make -f $SymEmuDIR/Makefile && make -f $SymEmuDIR/Makefile install
    # Go make some coffee or do whatever you want, this will take some time (approx. 60 mins on a 4-core machine)
```

By default, the ``make`` command compiles and installs μEmu in release mode to ``$SymEmuDIR/build/opt``. To change this
location, set the ``S2E_PREFIX`` environment variable when running ``make``.

To compile μEmu in debug mode, use ``make install-debug``.


### Updating

You can use the same Makefile to recompile μEmu either when changing it yourself or when pulling new versions through
``repo sync``. Note that the Makefile will not automatically reconfigure the packages; for deep changes you might need
to either start from scratch by issuing ``make clean`` or to force the reconfiguration of specific modules by deleting
the corresponding files from the ``stamps`` subdirectory.

## Usage

All μEmu plugins are enabled and configured with Lua-based configuration file `SymEmu-config.lua`.
To provide user a more user-friendly configuration file, we provide python script named `SymEmu-helper.py` to quickly generate Lua-base configure files based on template file `SymEmu-config-template.lua`  based on a sample user-defined CFG file.

It will also generate launch scripts to run SymEmu based on `launch-SymEmu-template.sh` file. 

Please make sure the `launch-SymEmu-template.sh`, `SymEmu-config-template.lua` and `library.lua` exist and place in the same path e.g., <proj_dir>  with `SymEmu-helper.py`.



### Preparing the user configuration file
You can use the configuration files provided in our [unit-tests](https://github.com/MCUSec/uEmu-unit_tests) and [real-world-firwmare](https://github.com/MCUSec/uEmu-real_world_firmware) repos to our unit test samples or real-world samples in the μEmu paper.
If you want to test your own firmware, please refer to this [instruction](docs/Configuration.md) and our paper to edit the user configuration file. 

Note that incorrect configurations will lead to unexpected  behaviors of μEmu like stall or finishing with inaccurate KB.


### μEmu workflow
Here, we take `WYCNINWYC.elf` firmware as a example to show how to run the μEmu with `SymEmu-helper.py` and some attention points in each phase.

#### KB Extraction Phase:
```bash
Usage: python3 <repo_path>SymEmu-helper.py ARMv7m <firmware_name> <config_file_name>  [-h] [--debug]
```

- arguments:
  * cpu                CPU Series. e.g., ARMv7m
  * firmware           Tested Firmware. e.g., drone.elf
  * config             User Configuration File. e.g., firmware.cfg
  * -h, --help (optional)           Show this help message and exit
  * --debug (optional)              Run μEmu in debug mode. Note that μEmu will output huge log information in a short time and slow down in debug mode, please ensure you have enough space (e.g., more than 100M). Thus, we recommend only run μEmu with debug mode under KB extraction phase.

**Example**:
```console
python3 <repo_path>/SymEmu-helper.py ARMv7m <proj_dir>/WYCINWYC.elf <proj_dir>/WYCNINWYC.cfg
```

After the above command successfully finishes,  you could find the `launch-SymEmu.sh` and `SymEmu-config.lua` in your <proj_dir>. Then, you can launch the first-round KB extraction via **carrying out the `launch-SymEmu.sh` script** and you can verify `SymEmu-config.lua` to know whether you configurations are actually as your excepted . 

After finishing (typically a few minutes), you can find log files and knowledge base (KB) file named as `firmwarename-roundnumber-finalstatenumber-unqiuebbnumber_KB.dat` (e.g., `WYCINWYC.elf-round1-state53-bbnum1069_KB.dat`) in `s2e-last` (referring to the `s2e-out-<max>`) folder. Detail logs will be printed to `s2e-last/debug.txt` and important log information will be printed to`s2e-last/warnings.txt` . More detail about log files please refer to [S2E documents](http://s2e.systems/docs/index.html) .

**NOTE**:
1. If you find μEmu cannot be finished KB extraction with a quiet long time (e.g., more than ten minutes), typically the reason is μEmu has been stuck. You should manually abort the execution, then check the configuration file, firmware and log files to find the reason and re-configure and re-run the firmware with μEmu. Thus,  we recommend user to enable debug level log information (add `--debug` in above command)  when he first time runs the firmware.



### Testcase analysis
If you only want to further analysis the firmware with single testcase input (e.g., crashing/hanging input), plese refer the below command to run μEmu helper script at first.

```bash
Usage: python3 <repo_path>/SymEmu-helper.py ARMv7m <firmware_name> <config_file_name>  -kb KBFILENAME -t TESTCASENAME
```
- arguments:
  * -t --testcasefilename,  Configure the testcase filename used for analysis and μEmu will exit when whole testcase has been consumed. If testcase filename is not present, μEmu will run fuzzing phase by default.


**Example**:

The below command is to configure μEmu for running `WYCINWYC.elf` firmware for single testcase analysis using `WYCINWYC.elf-round1-state53-tbnum1069_KB` KB file and testcase file `testcase.txt.`.
```console
python3 SymEmu-helper.py ARMv7m WYCINWYC.elf WYCNINWYC.cfg -kb WYCINWYC.elf-round1-state53-tbnum1069_KB.dat -t testcase.txt
```
### BB Coverage calcuation
When user manully terminates the fuzzing process, μEmu will automatically terminate and record all reached QEMU translate block start addresses and the execution frequency of each translation block in file `fuzz_tb_map.txt`.
We provide in this repo a IDA plugin named `idapy_dump_valid_basic_block_range.py` to output each basic block range in file `valid_basic_block_range.txt` and total number of basic blocks.
Then you can use `calculate.py` to get basic block coverage.
```bash
Usage: python3 calculate.py fuzz_tb_map.txt valid_basic_block_range.txt 
```
Coverage in publication paper = # of visited QEMU translation blocks / total # of basic blocks.

## Debugging with gdb
First, μEmu should be complied with both symbols and all debug information in order to use it with gdb:
```console
sudo make -f $SymEmuDIR/Makefile all-debug
```
Then, you can start μEmu in GDB with `./launch-SymEmu.sh debug`. The gdb configuration script `gdb.ini` will be automatically generated in your current folder.
More information about debugging, please refer to [DebuggingS2E](http://s2e.systems/docs/DebuggingS2E.html).

## More documentation
Please see [docs/](docs/) for more documentation.


## Issues
If you encounter any problems while using our tool, please open an issue. 

For other communications, you can email weizhou[at]hust.edu.cn.

