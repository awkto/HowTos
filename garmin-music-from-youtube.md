## How to get mp3s from Youtube playlist

1. Get **yt-dlp** binary for your system   
   https://github.com/yt-dlp/yt-dlp/releases/
2. Install yt-dlp in the right folder
   Place it in your **/usr/local/bin**
   ```
   sudo mv yt-dlp-linux /usr/loca/bin/yt-dlp
   ```
   Also make it executable with
   ```
   sudo chmod +x /usr/local/bin/yt-dlp
   ```

3. Run this command to pull mp3s from a youtube playlist
   ```
   yt-dlp -x --audio-format mp3 --audio-quality 320K [playlist_URL]
   ```
   #Note : url syntax https://www.youtube.com/playlist?list=[LIST_ID]
   
4. Install rename tool
   ```
   sudo apt install rename
   ```

5. Rename files to remove odd characters
   ```
   file-rename 's/[^A-Za-z0-9._-]+/_/g' -- *
   ```

## Create Playlists for multiple subdirectories
This works best if you have multiple youtube playlists you download and save them each in subfolders. This script will create a m3u playlist for each subdirectory.
1. Create this bash script in a file called **create-playlists.sh**
   ```bash
   #!/usr/bin/env bash
   for d in */; do
     # Skip if it's not a directory (in case of files matching the glob).
     [ -d "$d" ] || continue 
     # Collect all .mp3 files under subfolder 'd' (including deeper subfolders).
     find "$d" -type f -iname '*.mp3' | sort > "${d%/}.m3u"
   done
   ```

2. Make it executable
   ```
   chmod +x create-playlists.sh
   ```
3. Execute the script in the parent directory
   ```
   ./create-playlists.sh
   ```
