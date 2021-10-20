sudo apt-get update

# Initial build dependencies and packages are taken from:
#    https://github.com/S2E/s2e/blob/master/Dockerfile#L35
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get -y install build-essential cmake wget texinfo flex bison       \
    python-dev python3-dev python3-venv python3-distro mingw-w64 lsb-release

sudo apt-get update
sudo apt-get -y install libdwarf-dev libelf-dev libelf-dev:i386             \
    libboost-dev zlib1g-dev libjemalloc-dev nasm pkg-config                 \
    libmemcached-dev libpq-dev libc6-dev-i386 binutils-dev                  \
    libboost-system-dev libboost-serialization-dev libboost-regex-dev       \
    libbsd-dev libpixman-1-dev  libncurses5                                 \
    libglib2.0-dev libglib2.0-dev:i386 python3-docutils libpng-dev          \
    gcc-multilib g++-multilib gcc-9 g++-9

# Additional requirement required by clang
sudo apt-get install libtinfo5

# install git repo;
# 20.04 does only provide it as snap package, we opt in for manual installation
mkdir -p ~/.bin
PATH="${HOME}/.bin:${PATH}"
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/.bin/repo
chmod a+rx ~/.bin/repo

# setup env and directories
mkdir -p uemu/build
export uEmuDIR=$PWD/uemu

cd $uEmuDIR
~/.bin/repo init -u https://github.com/MCUSec/manifest.git -b uEmu
~/.bin/repo sync

# fix permissions
chmod +x $uEmuDIR/s2e/libs2e/configure

# get ptracearm.h
sudo wget -P /usr/include/x86_64-linux-gnu/asm \
    https://raw.githubusercontent.com/MCUSec/uEmu/main/ptracearm.h

# start build process
cd $uEmuDIR/build && make -f $uEmuDIR/Makefile
sudo make -f $uEmuDIR/Makefile install

cd $uEmuDIR/AFL
make
sudo make install

# Set up environment for new connections
echo "export uEmuDIR=$uEmuDIR" >> ~/.bashrc

# Installation done, get all repositories
cd $uEmuDIR
git clone https://github.com/MCUSec/uEmu-unit_tests.git
git clone https://github.com/MCUSec/uEmu-real_world_firmware.git
