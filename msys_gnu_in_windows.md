# Installing MSYS2 and Enabling GNU Tools in Windows

## Step 1: Install MSYS2

1. **Download MSYS2**:
   - Go to the [official MSYS2 website](https://www.msys2.org/).
   - Download the installer for your system (usually `msys2-x86_64-xxxxxx.exe` for 64-bit systems).

2. **Run the Installer**:
   - Double-click the downloaded installer and follow the installation prompts.
   - Choose the installation directory (the default is usually `C:\msys64`).

3. **Update the Package Database**:
   - After installation, open the MSYS2 shell (you can find it in the Start Menu as "MSYS2 MSYS").
   - Run the following commands to update the package database and core system packages:
     ```bash
     pacman -Syu
     ```
   - If prompted to close the terminal, do so, and then reopen the MSYS2 shell.

4. **Install the Required Packages**:
   - To install the GNU tools, you can install the base development packages. Run:
     ```bash
     pacman -S base-devel mingw-w64-x86_64-toolchain
     ```
   - This command installs essential development tools, including `gcc`, `make`, and other GNU utilities.

## Step 2: Add MSYS2 to User Environment Variables

1. **Open Environment Variables**:
   - Right-click on "This PC" or "My Computer" on the desktop or in File Explorer, and select "Properties."
   - Click on "Advanced system settings" on the left.
   - In the System Properties window, click on the **Environment Variables** button.

2. **Add MSYS2 to User Path**:
   - In the Environment Variables window, find the **Path** variable in the "User variables" section and select it, then click **Edit**.
   - In the Edit Environment Variable window, click **New** and add the path to the MSYS2 `bin` directory:
     ```
     C:\msys64\usr\bin
     ```
   - Click **OK** to close all dialog boxes.

## Optional Step: Modify System Path (if needed)

1. **Open Environment Variables**:
   - Follow the same steps as above to open the Environment Variables window.

2. **Add MSYS2 to System Path**:
   - In the Environment Variables window, find the **Path** variable in the "System variables" section and select it, then click **Edit**.
   - Click **New** and add the path to the MSYS2 `bin` directory:
     ```
     C:\msys64\usr\bin
     ```
   - You'll find that probably `C:\Windows\System32` is already in the list, so just move the MSYS path above it to ensure that the MSYS2 version of `bash` is called first.
   - Click **OK** to close all dialog boxes.

## Step 3: Open a New Command Prompt

After updating the PATH, open a new Command Prompt window (the changes won't apply to already open windows).

## Step 4: Test the Configuration

1. **Check Bash Version**:
   In the new Command Prompt window, type:
   ```cmd
   bash --version
