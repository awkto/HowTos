## How to Hide ImageMagick from Gnome Launcher

E.g You've got ImageMagick showing up in your Gnome launcher, but you don't use it directly and want it out of sight. The safest way to do this is to **hide its launcher icon** rather than fully uninstalling the software, as other applications often rely on it.

Here's how to do it:

1.  **Find its `.desktop` file:** Open your terminal and run this command to search inside common application directories for keywords related to ImageMagick:
    ```bash
    grep -ril "imagemagick" /usr/share/applications/
    ```
    * `grep`: The command for searching text.
    * `-r`: Searches **recursively** through all subdirectories.
    * `-i`: Performs a **case-insensitive** search.
    * `-l`: Lists **only the names of the files** that contain a match.
    * `"imagemagick"`: The pattern to search for.

    Look for a file like `/usr/share/applications/display-im6.q16.desktop` in the output. This is the one you want.
2.  **Copy the file to your local applications folder:** This makes sure your change won't be overwritten by system updates.
    ```bash
    cp /usr/share/applications/display-im6.q16.desktop ~/.local/share/applications/
    ```
    (Replace `/usr/share/applications/display-im6.q16.desktop` with the exact path you found in step 1 if it's different).
3.  **Edit the copied file:** Open the file you just copied in a text editor:
    ```bash
    nano ~/.local/share/applications/display-im6.q16.desktop
    ```
4.  **Add `NoDisplay=true`:** At the very end of the file, on its own new line, add:
    ```
    NoDisplay=true
    ```
    Save the file and close the editor.
5.  **Refresh Gnome Shell:** If it does not refresh after a minute, log out and log back in.

The ImageMagick icon should now be gone from your launcher!
