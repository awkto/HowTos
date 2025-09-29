## Linux Tools and Commands on Windows

How to set up Linux tools and commands on Windows so that you can call them directly from Powershell.

To set up MSYS2 in the Windows PATH so that PowerShell can directly call Linux binaries, follow these steps:

1. **Install MSYS2** : Download and install MSYS2 from msys2.org.
    
    https://www.msys2.org/#installation

2. **Update MSYS2** : Open the MSYS2 shell and run the following commands to update the package database and core system packages:
    ```
    pacman -Syu
    ```

3. Add **MSYS2** to PATH:
    - Open the Start Menu, search for "Environment Variables", and select "Edit the system environment variables".
    - In the System Properties window, click on "Environment Variables".
    - Under "System variables", find and select the Path variable, then click "Edit".
    - Click "New" and add the path to the MSYS2 usr/bin directory, typically `C:\msys64\usr\bin`

4. **Verify**: Open PowerShell and type a command like ls or bash to verify that MSYS2 binaries are accessible.

5. **Install Additional Tools**: If you need additional linux commands not installed by default, try installing it with
   ```
   pacman -S [package-name]
   ```
