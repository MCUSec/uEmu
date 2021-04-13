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
├── uEmu-helper.py           # helper scripts to configurate μEmu based on configration file (e.g., μEmu.cfg)
├── launch-uEmu-template.sh  # template scripts to launch μEmu
├── launch-AFL-template.sh   # template scripts to launch AFL fuzzer
├── uEmu-config-template.lua # template config file of μEmu and S2E plugins
├── library.lua              # Contains convenience functions for the uEmu-config.lua file.
├── uEmu-unit_tests          # uEmu unit test samples and config files
├── uEmu-fuzzing_tests       # uEmu fuzzing test samlpes (real-world MCU firmware) and config files
└── ptracearm.h
```


## Source Code Installation

**Note**:
1. uEmu builds and runs on Ubuntu 18.04 or 20.04 LTS (64-bit). Earlier versions may still work, but we do not support them anymore.

2. Since the qemu in arm kvm mode will use ptrace.h which is from the host arm linux kernel, however the real host μEmu is X86, so you have to add ptracearm.h from [linux source code](https://elixir.bootlin.com/linux/latest/source/arch/arm/include/asm/ptrace.h) (you can directly download it from this repo) to the your local path: ``/usr/include/x86_64-linux-gnu/asm``.

### Required packages

You must install a few packages in order to build μEmu manually.
The required packages of μEmu is same as the current S2E 2.0,
please check out [required packages](https://github.com/S2E/s2e/blob/master/Dockerfile#L35) of S2E.

**Note**:
please do not install S2E itself, but only install **build**, **S2E** and **C++17** dependencies.


### Checking out source code

The μEmu source code can be obtained from the my git repository using the following commands.

```console
 export uEmuDIR=/home/user/uEmu  # uEmuDIR must be in your home folder (e.g., /home/user/uEmu)
 sudo apt-get install git-repo   # or follow instructions at https://gerrit.googlesource.com/git-repo/
 cd $uEmuDIR
 repo init -u https://github.com/MCUSec/manifest.git -b uEmu
 repo sync
```
This will set up the μEmu repositories in ``$uEmuDIR``.


### Building μEmu

The μEmu Makefile can be run as follows:

```console
    $ sudo mkdir $uEmuDIR/build
    $ cd $uEmuDIR/build
    $ make -f $uEmuDIR/Makefile && sudo make install
    # Go make some coffee or do whatever you want, this will take some time (approx. 60 mins on a 4-core machine)
```

By default, the ``make`` command compiles and installs μEmu in release mode to ``$uEmuDIR/build/opt``. To change this
location, set the ``S2E_PREFIX`` environment variable when running ``make``.

To compile μEmu in debug mode, use ``make install-debug``.



### Building and Preparing AFL

```console
cd $uEmuDIR/AFL
make
sudo make install
```

### Updating

You can use the same Makefile to recompile μEmu either when changing it yourself or when pulling new versions through
``repo sync``. Note that the Makefile will not automatically reconfigure the packages; for deep changes you might need
to either start from scratch by issuing ``make clean`` or to force the reconfiguration of specific modules by deleting
the corresponding files from the ``stamps`` subdirectory.

## Usage

All  μEmu plugins are enabled and configured with Lua-based configuration file `uEmu-config.lua`.
To provide user a more user-friendly configuration file, we provide python script named `uEmu-helper.py` to quickly generate Lua-base configure files based on template file `uEmu-config-template.lua`  based on a sample user-defined CFG file.

It will also generate launch scripts to run μEmu and AFL fuzzer based on `launch-uEmu-template.sh` and `launch-AFL-template.sh` files. 

Please make sure the `launch-uEmu-template.sh`, `launch-AFL-template.sh`, `uEmu-config-template.lua` and `library.lua` exist and place in the same path e.g., <proj_dir>  with `uEmu-helper.py`.



```bash
Usage: python3 <repo_path>/uEmu-helper.py <firmware_name> <config_file_name>  [-h] [--debug] [-kb KBFILENAME] [-s SEEDFILENAME]
```

- positional arguments:
  * firmware           Tested Firmware. e.g., drone.elf
  * config                User Configuration File. e.g., firmware.cfg

- optional arguments:
  * -h, --help            Show this help message and exit
  * --debug               Run μEmu in debug mode. Note that μEmu will output huge log information in a short time and slow down in debug mode, , please ensure you have enough space (e.g., more than 100M). Thus, we recommend only run μEmu with debug mode under KB extraction phase or the beginning of fuzzing phase.
  * -kb KBFILENAME,       Configure the Knowledge Base filename used for μEmu fuzzing phase and μEmu will run under fuzzing phase. If KB file is not present, μEmu will run KB extraction phase by default.
  * -s SEEDFILENAME,      Configure the seed filename to bootstrap fuzzing, if absent, μEmu will use random number for fuzzing.

### Preparing the user configuration file
You can use the configuration files provided in our [unit-tests](https://github.com/MCUSec/uEmu-unit_tests) and [real-world-firwmare](https://github.com/MCUSec/uEmu-read_world_firmware) repos to our unit test samples or real-world samples in the μEmu paper.
If you want to test your own firmware, please refer to this [instruction](docs/config.md) and our paper to edit the user configuration file. 

Note that incorrect configurations will lead to unexpected  behaviors of μEmu like stall or finishing with inaccurate KB.


### Example of μEmu workflow
Here, we take `WYCNINWYC.elf` firmware as a example to show how to run the μEmu with `uEmu-helper.py` and some attention points in each phase.

#### KB Extraction Phase:
```console
python3 <repo_path>/uEmu-helper.py <proj_dir>/WYCINWYC.elf <proj_dir>/WYCNINWYC.cfg
```

After the above command successfully finishes,  you could find the `launch-uEmu.sh` and `uEmu-config.lua` in your <proj_dir>. Then, you can launch the first-round KB extraction via carry out the `launch-uEmu.sh` script and you can check `uEmu-config.lua` to know whether you configurations are actually as your excepted . 

After finishing (typically a few minutes), you can find log files and knowledge base (KB) file (e.g., `WYCINWYC.elf-round1-state53-tbnum1069_KB.dat`) in `s2e-last` (referring to the `s2e-out-<max>`) folder. Detail logs will be printed to `s2e-last/debug.txt` and important log information will be printed to`s2e-last/warnings.txt` . More detail about log files please refer to [S2E documents](http://s2e.systems/docs/index.html) .

**NOTE**:

1. If you find μEmu cannot be finished KB extraction with a quiet long time (e.g., more than ten minutes), typically the reason is μEmu has been stuck. You should manually abort the execution, then check the configuration file, firmware and log files to find the reason and re-configure and re-run the firmware with μEmu. Thus,  we recommend user to enable debug level log information (add `--debug` in above command)  when he first time runs the firmware.


#### Dynamic Analysis and Fuzzing Phase:

Next, you can run the firmware with learned KB for dynamic analysis.  About more detail about KB entries format please refer to [kb.md](docs/KB.md).

The below command is to configure μEmu for running `WYCINWYC.elf` firmware in dynamic phase with `WYCINWYC.elf-round1-state53-tbnum1069_KB` KB file and fuzzing seed file `small_document.xml`.


```console
python3 uEmu-helper.py WYCINWYC.elf WYCNINWYC.cfg -kb WYCINWYC.elf-round1-state53-tbnum1069_KB.dat -s small_document.xml
```
Since μEmu relies on AFL for fuzzing input. Thus, you first need to launch AFL fuzzur via `./launch-AFL.sh` in one terminal to input test-cases and then launch μEmu via `./launch-uEmu.sh` in another terminal to consume the test-cases.
The fuzzing results is stored in <proj_dir>/<firmware> folder. The log and KB files of addition round KB extraction phase are record in <s2e-last> folder.

**NOTE**:
1. Please abort fuzzing from AFL terminal, and then μEmu will automatically terminate.
1. We recommend enable `auto_mode_switch`  in configuration file during fuzzing to automatically switch two phase , since complex firmware often use new peripherals on demand.
2. If no seed file given, μEmu will use 4 bytes random number as initial seed to bootstrap fuzzing.
3. We enable fuzzing test during dynamic analysis phase by default, but user can disable it (`enable_fuzz = false`) in configuration file. Then data registers will only used values from KB.
4. For more advanced configurations during fuzzing phase, please refer to `Fuzzer_Config` section in [instruction](docs/config.md).

## Debugging with gdb
First, μEmu should be complied with both symbols and all debug information in order to use it with gdb:
```console
sudo make -f $uEmuDIR/Makefile all-debug
```
Then, you can start μEmu in GDB with `./launch-uEmu.sh debug`. The gdb configuration script `gdb.ini` will be automatically generated in your current folder.
More information about debugging, please refer to [DebuggingS2E](http://s2e.systems/docs/DebuggingS2E.html).

## More documentation
Please see [docs/](docs/) for more documentation.


## Issues
If you encounter any problems while using our tool, please open an issue. 

For other communications, you can email zhouw[at]nipc.org.cn.

## TODOs

### Docker installation

## Help Wanted

### DMA Support
### Architectures beyond ARM Cortex-M
### Firmware Analysis beyond Fuzzing
