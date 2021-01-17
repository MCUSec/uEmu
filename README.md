# uEmu
A Micro Emulator for In-Vivo Analysis of Embedded Devices without Any Hardware Dependence

## Notice

## Building uEmu manually
**NOTE**:
1. If you are using Ubuntu 14.04 you must install CMake manually - S2E requires version 3.4.3 or newer, which is
not available in the Ubuntu 14.04 repositories.

2. The uEmu is still compatianle with the original S2E, so you can also analyze i386 and X64 program

3. Since the qemu in arm kvm mode will use ptrace.h which is from the host arm linux kernel, however the real host uEmu is X86, so you have to add ptracearm.h from [linux source code](https://elixir.bootlin.com/linux/latest/source/arch/arm/include/asm/ptrace.h) (you can also directly download it from this repo) to the your local path: /usr/include/x86_64-linux-gnu/asm 

### Required packages

You must install a few packages in order to build uEmu manually.
The required packages of uEmu is same as the current S2E 2.0,
please check out [required packages](http://s2e.systems/docs/BuildingS2E.html#required-packages) of S2E.

### Checking out uEmu

The uEmu source code can be obtained from the my git repository using the following commands.

    # uEmuDIR must be in your home folder (e.g., /home/user/uEmu)
    cd $uEmuDIR
    sudo repo init -u git://github.com/weizhou-chaojixx/manifest.git -b uEmu
    sudo repo sync

This will set up the S2E repositories in ``$uEmuDIR``.


### Building

The uEmu Makefile can be run as follows:


    sudo mkdir $uEmuDIR/build
    cd $uEmuDIR/build
    sudo make -f $uEmuDIR/Makefile install

    # Go make some coffee or do whatever you want, this will take some time (approx. 60 mins on a 4-core machine)

By default, the ``make`` command compiles and installs uEmu in release mode to ``$uEmuDIR/build/opt``. To change this
location, set the ``S2E_PREFIX`` environment variable when running ``make``.

To compile uEmu in debug mode, use ``make install-debug``.

Note that the Makefile automatically uses the maximum number of available processors in order to speed up compilation.

### Updating

You can use the same Makefile to recompile S2E either when changing it yourself or when pulling new versions through
``repo sync``. Note that the Makefile will not automatically reconfigure the packages; for deep changes you might need
to either start from scratch by issuing ``make clean`` or to force the reconfiguration of specific modules by deleting
the corresponding files from the ``stamps`` subdirectory.

## Usage
