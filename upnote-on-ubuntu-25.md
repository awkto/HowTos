## How to Install UpNote on Ubuntu 25 Using AppImage Launcher

This guide will help you install AppImage Launcher and use it to install and run UpNote on Ubuntu 25.

<br>

### Step 1: Install AppImage Launcher

1. **Download AppImage Launcher**: You can download the latest AppImage Launcher from the [AppImage Launcher GitHub Releases page](https://github.com/TheAssassin/AppImageLauncher/releases).
2. **Install AppImage Launcher**: After downloading the `.deb` package, install it using the following command (replace `appimagelauncher_*.deb` with the actual filename):

```bash
sudo dpkg -i ~/Downloads/appimagelauncher_*.deb
```

If there are any dependency issues, you can resolve them with:

```bash
sudo apt install -f
```

<br>

### Step 2: Download UpNote AppImage

1. Download the UpNote AppImage from the official website or repository.
2. Save the AppImage file to your desired location (e.g., `~/Applications`).

<br>

### Step 3: Use AppImage Launcher to Integrate UpNote

1. Navigate to the directory where the UpNote AppImage is located:

```bash
cd ~/Applications
```
2. Run the UpNote AppImage by double-clicking it in your file manager or using the terminal:

```bash
./UpNote_*.AppImage
```
3. When prompted by AppImage Launcher, click the **"Integrate and Run"** button. This will integrate UpNote into your system, allowing you to launch it from your application menu.

<br>

### Step 4: Run UpNote

After integration, you can find UpNote in your application menu. Click on it to launch the application.

<br>

## Conclusion

You should now have UpNote installed and integrated into your Ubuntu 25 system using AppImage Launcher. If you encounter any issues, feel free to seek further assistance.

<br>
