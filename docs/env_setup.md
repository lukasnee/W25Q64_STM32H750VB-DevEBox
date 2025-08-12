
# Environment Setup

Building, flashing and debugging the firmware requires a specific environment
setup. Please follow the following sections to set up your development
environment.

## Firmware Development Environment

These are the tools required for building the firmware:

1. Install Ninja build system:

    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y git ninja-build
    ```

2. Install CMake. Note that running `sudo apt install cmake` may install an
   older version of CMake than 4.0.0. Instead, you may want to install the latest
   CMake from [here](https://cmake.org/download/). For example:

    ```bash
    VERSION=$(curl -s https://api.github.com/repos/Kitware/CMake/releases/latest | grep -Po '"tag_name": "v\K[^"]*')
    cd /tmp/
    wget https://github.com/Kitware/CMake/releases/download/v$VERSION/cmake-$VERSION-linux-x86_64.sh
    sudo sh cmake-$VERSION-linux-x86_64.sh --skip-license --prefix=/usr/local/
    ```

3. Install Arm GNU toolchain:

    ```bash
    VERSION=$(curl -s https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads | grep -Po '<h4>Version \K.+(?=</h4>)')
    curl -Lo gcc-arm-none-eabi.tar.xz "https://developer.arm.com/-/media/Files/downloads/gnu/${VERSION}/binrel/arm-gnu-toolchain-${VERSION}-x86_64-arm-none-eabi.tar.xz"
    sudo mkdir /opt/gcc-arm-none-eabi
    sudo tar xf gcc-arm-none-eabi.tar.xz --strip-components=1 -C /opt/gcc-arm-none-eabi
    echo 'export PATH=$PATH:/opt/gcc-arm-none-eabi/bin' | sudo tee -a /etc/profile.d/gcc-arm-none-eabi.sh
    source /etc/profile
    arm-none-eabi-gcc --version
    arm-none-eabi-g++ --version
    arm-none-eabi-gdb --version
    rm -rf gcc-arm-none-eabi.tar.xz
    ```

    If getting `arm-none-eabi-gdb: error while loading shared libraries:
    libncursesw.so.5` error, install `libncurses5`:

    ```bash
    sudo apt install -y libncurses5
    ```

    If that does not help, try this:

    ```bash
    sudo apt install -y gdb-multiarch
    sudo mv /usr/bin/arm-none-eabi-gdb /usr/bin/arm-none-eabi-gdb.bak
    sudo ln -s /usr/bin/gdb-multiarch /usr/bin/arm-none-eabi-gdb
    ```

## ST-LINK Tools

ST-LINK tools can be used to flash and debug the firmware.

```bash
sudo apt install stlink-tools
```

## J-Link Software and Documentation Pack

J-Link tools can be used to flash and debug the firmware (preferred over
ST-LINK).

1. Go to [SEGGER J-Link Software and Documentation Pack](https://www.segger.com/downloads/jlink/#J-LinkSoftwareAndDocumentationPack)

2. Download `64-bit DEB Installer`.

3. Install the downloaded package:

    ```bash
    sudo dpkg -i JLink_Linux_V<XXX>_x86_64.deb
    echo 'export PATH=/opt/SEGGER/JLink:$PATH' >> ~/.bashrc
    source ~/.bashrc
    ```

## Python Virtual Environment

We need a Python virtual environment for protobuf generation and
[`tools/comm/comm.py`](../tools/comm/comm.py) library.

```bash
sudo apt update && sudo apt -y upgrade
sudo apt install python3
python3 -m venv .venv
.venv/bin/pip install --upgrade pip setuptools
.venv/bin/pip install -r requirements.txt
```

> [!Note]
>
> You can also run `source .venv/bin/activate.fish` for fish shell or `source
> .venv/bin/activate` for bash/zsh to activate the virtual environment in your
> current terminal session so you don't have to prefix every `python` or `pip`
> command with `.venv/bin/`.
