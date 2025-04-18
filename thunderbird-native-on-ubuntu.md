# Installing Thunderbird from a `.tar.gz` File on Ubuntu

Follow these steps to install Thunderbird on your Ubuntu system using a `.tar.gz` file.

<br>

## Step 1: Download the Thunderbird `.tar.gz` File

You can download the latest version of Thunderbird from the official website. Use your web browser or the command line with `wget`. For example:

```bash
wget https://download.mozilla.org/?product=thunderbird-latest-ssl&os=linux64&lang=en-US -O thunderbird.tar.gz
```

<br>

## Step 2: Extract the `.tar.gz` File

Open a terminal and navigate to the directory where you downloaded the file. Then, extract it using the following command:

```bash
tar -xvzf thunderbird.tar.gz
```

<br>

## Step 3: Move the Extracted Folder

You can move the extracted Thunderbird folder to a more appropriate location, such as `/opt`:

```bash
sudo mv thunderbird /opt/
```

<br>

## Step 4: Create a Symbolic Link (Optional)

To make it easier to run Thunderbird from the terminal, you can create a symbolic link:

```bash
sudo ln -s /opt/thunderbird/thunderbird /usr/bin/thunderbird
```

<br>

## Step 5: Run Thunderbird

You can now run Thunderbird by typing `thunderbird` in the terminal:

```bash
thunderbird
```

<br>

## Step 6: Create a Desktop Entry (Optional)

If you want to add Thunderbird to your applications menu, create a `.desktop` file:

```bash
sudo nano /usr/share/applications/thunderbird.desktop
```

Add the following content to the file:

```ini
[Desktop Entry]
Name=Thunderbird
Exec=/opt/thunderbird/thunderbird
Icon=/opt/thunderbird/chrome/icons/default/default128.png
Type=Application
Categories=Application;Network;Email;
```

Save and exit the editor (in nano, press `CTRL + X`, then `Y`, and `Enter`).

<br>

## Step 7: Launch Thunderbird

You should now see Thunderbird in your applications menu, and you can launch it from there.

* * *

That's it! You have successfully installed Thunderbird from a `.tar.gz` file on Ubuntu.
