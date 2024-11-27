c# How to Run Neofetch on Harvester
Neofetch is a lightweight system information tool that provides a sleek overview of your system, including OS, kernel, CPU, memory, and more. Harvester's immutable system design makes installing packages challenging, but Neofetch can be run as a portable script without installation.

Follow this guide to run Neofetch on a Harvester system.

## Steps to Run Neofetch on Harvester
1. Download Neofetch as a Portable Script
Log in to your Harvester system and download the Neofetch script directly from its official GitHub repository:

```bash
curl https://raw.githubusercontent.com/dylanaraps/neofetch/master/neofetch -o neofetch
```
2. Make the Script Executable
After downloading, you need to give the script executable permissions:

```bash
chmod +x neofetch
```

3. Run Neofetch
Execute the Neofetch script to display system information:

```bash
./neofetch
```

Example Output
Here’s what you can expect when running Neofetch:

```
           .;ldkO0000Okdl;.              root@harvester2 
       .;d00xl:^''''''^:ok00d;.          --------------- 
     .d00l'                'o00d.        OS: SUSE Linux Enterprise Micro for Rancher 5.4 x86_64 
   .d0Kd'  Okxol:;,.          :O0d.      Host: LENOVO 316E 
  .OKKKK0kOKKKKKKKKKKOxo:,      lKO.     Kernel: 5.14.21-150400.24.108-default 
 ,0KKKKKKKKKKKKKKKK0P^,,,^dx:    ;00,    Uptime: 58 mins 
.OKKKKKKKKKKKKKKKKk'.oOPPb.'0k.   cKO.   Packages: 419 (rpm) 
:KKKKKKKKKKKKKKKKK: kKx..dd lKd   'OK:   Shell: bash 4.4.23 
dKKKKKKKKKKKOx0KKKd ^0KKKO' kKKc   dKd   CPU: Intel i5-10400T (12) @ 3.600GHz 
dKKKKKKKKKKKK;.;oOKx,..^..;kKKK0.  dKd   GPU: Intel CometLake-S GT2 [UHD Graphics 630] 
:KKKKKKKKKKKK0o;...^cdxxOK0O/^^'  .0K:   Memory: 8284MiB / 31812MiB 
 kKKKKKKKKKKKKKKK0x;,,......,;od  lKk
 '0KKKKKKKKKKKKKKKKKKKKK00KKOo^  c00'                            
  'kKKKOxddxkOO00000Okxoc;''   .dKk'                             
    l0Ko.                    .c00l'
     'l0Kk:.              .;xK0l'
        'lkK0xl:;,,,,;:ldO0kl'
            '^:ldxkkkkxdl:^'
```
## Notes
1. **Dependencies**: Neofetch requires common utilities like bash, grep, and awk, which are preinstalled on Harvester.
2. **No Installation**: Since the script runs standalone, you don't need to use zypper or modify Harvester's immutable filesystem.
3. **Temporary Usage**: The downloaded script resides in your session and won’t persist across reboots unless stored in a writable location.

## Optional: Store the Script for Persistent Use
To keep Neofetch available across reboots, copy the script to a writable directory, such as /var/lib/rancher/:

```bash
sudo cp neofetch /var/lib/rancher/
sudo chmod +x /var/lib/rancher/neofetch
```

Then, run it using:

```bash
/var/lib/rancher/neofetch
```

Now you can easily check system details on your Harvester cluster using Neofetch without altering its immutable design!
