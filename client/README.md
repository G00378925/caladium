<!-- 9:09 PM 20-02-2023 -->
# Client

This directory contains the client application for Caladium.
The Python source code can be found in the `src` directory.

`caladium.spec` contains the pyinstaller config for bundling the client into an executable.
`caladium.sed` contains the config for iexpress.exe, which is used to create the installer.

## Building

To build the client, run the following command, (use must be on Windows, because iexpress.exe is used):

    build.cmd

This will create a `dist` directory containing an installer called `caladium-setup.exe`.
Before building make sure you have the latest version of Python, pyinstaller and tkthread installed:

    pip install -r requirements.txt

## Credits

Pill icon is from: [https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053](https://freeicons.io/healthcare-2/healthcare-medical-pill-icon-43053)
