# SACA Windows App Demo Build

This folder can be published into a portable Windows demo package so you can run the app without opening Visual Studio.

## What you Need

- Windows 10 or Windows 11.
- The backend service running at `http://127.0.0.1:8000`.
- A microphone if they want to test voice input.

The published app is self-contained, so teammates do not need to install the .NET runtime separately.


## Run The Demo App

1. Unzip `SACA.WindowsApp-win-x64.zip`.
2. Start the backend service first.
3. Open the extracted folder.
4. Double-click `SACA.WindowsApp.exe`.

If Windows SmartScreen appears, choose `More info`, then `Run anyway`.

## Common Issues

If the app opens but prediction or voice does not work, check that the backend is running at `http://127.0.0.1:8000`.

If voice recording does not work, check Windows microphone permission and choose a working input device.

If the app cannot start from a network drive, copy the extracted folder to a local folder such as Desktop or Documents and run it again.
