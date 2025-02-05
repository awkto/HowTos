# Mount an R2 storage from Cloudflare

1. Create an **R2 storage** and **bucket** on Cloudflare
2. Create an **API key** there as well
3. Install **rclone** on ubuntu
4. Edit your rclone config
   ```
   nano ~/.config/rclone/rclone.conf
   ```
5. Add these lines
   ```
   [r2]
   type = s3
   provider = Cloudflare
   access_key_id = YOUR_ACCESS_KEY
   secret_access_key = YOUR_SECRET_KEY
   endpoint = https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
   ```
6. Make a directory and mount your bucket
   ```
   mkdir -p /mnt/mybucket
   rclone mount r2:mybucket /mnt/mybucket --daemon
   ```
7. Add auto mount on boot via crontabb
   ```
   crontab -e
   ```
8. Add this line to the bottom and save
   ```
   @reboot rclone mount r2:mybucket /mnt/mybucket --daemon
   ```
9. Now add your files into the mounted dir **/mnt/mybucket**
10. To force RCLONE to sync or skip the delay
   ```
   rclone sync /mnt/mybucket r2:mybucket --progress
   ```
