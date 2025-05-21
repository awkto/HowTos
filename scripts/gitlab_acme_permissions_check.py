import os
import subprocess
import re
import pwd
import grp
import sys

# --- Color Codes ---
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m' # No Color

# --- Configuration ---
ACME_SH_USER = os.getenv('SUDO_USER') or os.getlogin() # Get the original user if run via sudo, else current login
ACME_SH_HOME = f"/home/{ACME_SH_USER}/.acme.sh"
GITLAB_SSL_DIR = "/etc/gitlab/ssl"
GITLAB_RB_PATH = "/etc/gitlab/gitlab.rb"
SSLADMINS_GROUP = "ssladmins"
GITLAB_CTL_PATH = "/usr/bin/gitlab-ctl"
CHMOD_PATH = "/bin/chmod"

# --- Helper Functions ---
def print_header(title):
    print(f"\n{Colors.BLUE}--- {title} ---{Colors.NC}")

def print_status(status, message):
    if status == "OK":
        print(f"  {Colors.GREEN}✓ OK{Colors.NC}: {message}")
    elif status == "FAIL":
        print(f"  {Colors.RED}✗ FAIL{Colors.NC}: {message}")
    elif status == "WARN":
        print(f"  {Colors.YELLOW}! WARN{Colors.NC}: {message}")
    else: # Fallback for unexpected status
        print(f"  {message}")

def run_sudo_command(command_list, check=True, capture_output=False):
    """
    Runs a command with sudo.
    If check is True, raises CalledProcessError on non-zero exit code.
    """
    try:
        result = subprocess.run(
            ['sudo'] + command_list,
            check=check,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            errors='replace' # Handle potential decoding errors
        )
        return result
    except subprocess.CalledProcessError as e:
        print_status("FAIL", f"Sudo command failed: {' '.join(command_list)}")
        if capture_output:
            print(f"    Stdout: {e.stdout.strip()}")
            print(f"    Stderr: {e.stderr.strip()}")
        raise # Re-raise to indicate failure to the caller
    except FileNotFoundError:
        print_status("FAIL", f"Sudo or command not found: {' '.join(command_list)}")
        raise # Re-raise
    except Exception as e:
        print_status("FAIL", f"Unexpected error running sudo command: {e} -> {' '.join(command_list)}")
        raise # Re-raise


def check_user_in_group(user, group):
    print(f"  Checking if user '{user}' is in group '{group}'... ", end='')
    try:
        groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
        # Also check if user's primary group is the target group
        user_info = pwd.getpwnam(user)
        try:
            if user_info.pw_gid == grp.getgrnam(group).gr_gid:
                groups.append(group) # Add primary group if it matches
        except KeyError:
            pass # Group might not exist yet, handled by outer check

        if group in groups:
            print_status("OK", f"User '{user}' is in group '{group}'.")
            return True
        else:
            print_status("FAIL", f"User '{user}' is NOT in group '{group}'. (Current groups: {', '.join(groups)})")
            return False
    except KeyError:
        print_status("FAIL", f"Group '{group}' or user '{user}' does not exist. Please create them.")
        return False
    except Exception as e:
        print_status("FAIL", f"Error checking group membership: {e}")
        return False

def check_file_permissions(file_path, expected_perms, expected_owner, expected_group, file_type):
    print(f"  Checking {file_type} permissions for {file_path}... ", end='')
    if not os.path.exists(file_path):
        print_status("WARN", f"{file_type} does not exist. (Skipping detailed permission check)")
        return True # Not a failure for the check itself

    try:
        # Use sudo stat to get permissions for root-owned files
        stat_result = run_sudo_command(['stat', '-c', '%a %U %G', file_path], capture_output=True)
        perms, owner, group = stat_result.stdout.strip().split()

        status = "OK"
        issues = []

        if perms != expected_perms:
            issues.append(f"Permissions: Current={perms}, Expected={expected_perms}")
            status = "FAIL"
        if owner != expected_owner:
            issues.append(f"Owner: Current={owner}, Expected={expected_owner}")
            status = "FAIL"
        if group != expected_group:
            issues.append(f"Group: Current={group}, Expected={expected_group}")
            status = "FAIL"

        if status == "OK":
            print_status("OK", f"Perms: {perms}, Owner: {owner}, Group: {group}")
            return True
        else:
            print_status("FAIL", f"Perms: {perms}, Owner: {owner}, Group: {group}")
            for issue in issues:
                print(f"    - {Colors.RED}{issue}{Colors.NC}")
            return False
    except subprocess.CalledProcessError:
        # run_sudo_command already printed FAIL
        return False
    except Exception as e:
        print_status("FAIL", f"Error checking file permissions: {e}")
        return False

def check_sudo_nopasswd(cmd_name, cmd_path):
    print(f"  Checking sudo NOPASSWD for '{cmd_name}' ({cmd_path})... ", end='')
    try:
        # Test with -n (no password) and a harmless flag like --help or -v
        # Ensure command exists before attempting sudo -n on it
        if not os.path.exists(cmd_path):
            print_status("FAIL", f"Command '{cmd_name}' not found at '{cmd_path}'.")
            return False

        # Attempt to run a command that will *always* succeed if NOPASSWD works
        # and will fail if password is required. Use a very short timeout.
        test_command = [cmd_path]
        if cmd_name == "gitlab-ctl":
            test_command = [cmd_path, "status"] # gitlab-ctl status is relatively safe
        elif cmd_name == "chmod":
            test_command = [cmd_path, "--version"] # --version is generally safe for core utils

        result = subprocess.run(
            ['sudo', '-n'] + test_command,
            capture_output=True, text=True, timeout=5,
            encoding='utf-8', errors='replace'
        )

        if result.returncode == 0:
            print_status("OK", f"NOPASSWD for '{cmd_name}' is configured.")
            return True
        else:
            # If returncode is not 0, it means it might have failed for other reasons
            # but -n means it didn't prompt for password.
            # We specifically look for the "password required" message in stderr.
            if "password is required" in result.stderr.lower():
                print_status("FAIL", f"NOPASSWD for '{cmd_name}' is NOT configured. (Password likely required. Check sudoers.)")
                return False
            else:
                # Command failed, but not due to NOPASSWD. Still a potential issue.
                print_status("WARN", f"NOPASSWD for '{cmd_name}' seems configured, but command had issues: {result.stderr.strip()}")
                return True # Assume NOPASSWD is fine, but command itself has issues.
    except subprocess.TimeoutExpired:
        print_status("FAIL", f"NOPASSWD for '{cmd_name}' timed out. (Might be prompting for password or stuck)")
        return False
    except FileNotFoundError:
        print_status("FAIL", f"Sudo or command not found to test NOPASSWD for '{cmd_name}'.")
        return False
    except Exception as e:
        print_status("FAIL", f"Error checking NOPASSWD for '{cmd_name}': {e}")
        return False

def parse_gitlab_rb():
    print_header(f"Parsing {GITLAB_RB_PATH} for SSL configuration")
    gitlab_fqdn = ""
    gitlab_cert_file = ""
    gitlab_key_file = ""

    try:
        # Read gitlab.rb using sudo
        result = run_sudo_command(['cat', GITLAB_RB_PATH], capture_output=True)
        content = result.stdout

        # Regex to extract values, handling single/double quotes and stripping
        # Adjusted regex to correctly capture content within single or double quotes
        fqdn_match = re.search(r"^\s*external_url\s*['\"]?(?:https?://)?([^'\"/]+)[/]*['\"]?\s*$", content, re.MULTILINE)
        if fqdn_match:
            gitlab_fqdn = fqdn_match.group(1) # Capture the FQDN directly

        cert_match = re.search(r"^\s*nginx\['ssl_certificate'\]\s*=\s*['\"]([^'\"]+)['\"].*", content, re.MULTILINE)
        if cert_match:
            gitlab_cert_file = cert_match.group(1)

        key_match = re.search(r"^\s*nginx\['ssl_certificate_key'\]\s*=\s*['\"]([^'\"]+)['\"].*", content, re.MULTILINE)
        if key_match:
            gitlab_key_file = key_match.group(1)

    except subprocess.CalledProcessError:
        print_status("FAIL", f"Could not read {GITLAB_RB_PATH}. (Check sudo permissions for cat)")
        return "", "", ""
    except Exception as e:
        print_status("FAIL", f"Error parsing {GITLAB_RB_PATH}: {e}")
        return "", "", ""

    return gitlab_fqdn, gitlab_cert_file, gitlab_key_file

def main():
    print_header("acme.sh GitLab SSL Permission Checker")
    print(f"Running as user: {ACME_SH_USER}")
    print("--------------------------------------------------------")

    # --- Step 1: Get GitLab FQDN and SSL paths ---
    GITLAB_FQDN, GITLAB_CERT_FILE, GITLAB_KEY_FILE = parse_gitlab_rb()

    # Fallback/validation for FQDN if parsing fails or is incomplete
    if not GITLAB_FQDN:
        print_status("WARN", f"Could not automatically detect GitLab FQDN from {GITLAB_RB_PATH}.")
        user_input_fqdn = input(f"Please manually enter your GitLab FQDN (e.g., gitlab.example.com): ")
        if not user_input_fqdn:
            print_status("FAIL", "GitLab FQDN is required. Exiting.")
            sys.exit(1)
        GITLAB_FQDN = user_input_fqdn.strip().lower().replace("https://", "").replace("http://", "").split('/')[0]

    # Fallback/validation for cert/key paths
    if not GITLAB_CERT_FILE:
        print_status("WARN", f"Could not automatically detect SSL certificate path from {GITLAB_RB_PATH}. Assuming {GITLAB_SSL_DIR}/{GITLAB_FQDN}.cer")
        GITLAB_CERT_FILE = f"{GITLAB_SSL_DIR}/{GITLAB_FQDN}.cer"
    if not GITLAB_KEY_FILE:
        print_status("WARN", f"Could not automatically detect SSL key path from {GITLAB_RB_PATH}. Assuming {GITLAB_SSL_DIR}/{GITLAB_FQDN}.key")
        GITLAB_KEY_FILE = f"{GITLAB_SSL_DIR}/{GITLAB_FQDN}.key"

    print(f"Using GitLab FQDN: {Colors.BLUE}{GITLAB_FQDN}{Colors.NC}")
    print(f"GitLab Certificate File: {Colors.BLUE}{GITLAB_CERT_FILE}{Colors.NC}")
    print(f"GitLab Key File: {Colors.BLUE}{GITLAB_KEY_FILE}{Colors.NC}")
    print("--------------------------------------------------------")

    # --- Part 1: User and Group Permissions ---
    print_header("Part 1: User and Group Permissions")
    check_user_in_group(ACME_SH_USER, SSLADMINS_GROUP)

    # --- Part 2: Directory and File Permissions for GitLab SSL ---
    print_header("Part 2: Directory and File Permissions for GitLab SSL")
    check_file_permissions(GITLAB_SSL_DIR, "770", "root", SSLADMINS_GROUP, "GitLab SSL Directory")

    # Certificate File Check
    print(f"  Checking Certificate File ({GITLAB_CERT_FILE})... ", end='')
    if os.path.exists(GITLAB_CERT_FILE):
        try:
            stat_result = run_sudo_command(['stat', '-c', '%a %U %G', GITLAB_CERT_FILE], capture_output=True)
            perms, owner, group = stat_result.stdout.strip().split()

            if perms == "644" and owner == "root" and group == "root":
                print_status("OK", f"Perms: {perms}, Owner: {owner}, Group: {group} (Secure)")
            elif perms == "664" and owner == "root" and group == SSLADMINS_GROUP:
                print_status("WARN", f"Perms: {perms}, Owner: {owner}, Group: {group} (Writable by {SSLADMINS_GROUP} for acme.sh, should be secured to 644 root root by reloadcmd)")
            else:
                print_status("FAIL", f"Perms: {perms}, Owner: {owner}, Group: {group}")
                print(f"    - {Colors.RED}Expected 644 root root, or 664 root {SSLADMINS_GROUP} during deployment.{Colors.NC}")
        except subprocess.CalledProcessError:
            pass # Error already printed by run_sudo_command
        except Exception as e:
            print_status("FAIL", f"Error checking certificate file: {e}")
    else:
        print_status("WARN", "Certificate File does not exist. (Skipping detailed permission check)")

    # Private Key File Check
    print(f"  Checking Private Key File ({GITLAB_KEY_FILE})... ", end='')
    if os.path.exists(GITLAB_KEY_FILE):
        try:
            stat_result = run_sudo_command(['stat', '-c', '%a %U %G', GITLAB_KEY_FILE], capture_output=True)
            perms, owner, group = stat_result.stdout.strip().split()

            if perms == "600" and owner == "root" and group == "root":
                print_status("OK", f"Perms: {perms}, Owner: {owner}, Group: {group} (Secure)")
            elif perms == "660" and owner == "root" and group == SSLADMINS_GROUP:
                print_status("WARN", f"Perms: {perms}, Owner: {owner}, Group: {group} (Writable by {SSLADMINS_GROUP} for acme.sh, should be secured to 600 root root by reloadcmd)")
            else:
                print_status("FAIL", f"Perms: {perms}, Owner: {owner}, Group: {group}")
                print(f"    - {Colors.RED}Expected 600 root root, or 660 root {SSLADMINS_GROUP} during deployment.{Colors.NC}")
        except subprocess.CalledProcessError:
            pass # Error already printed by run_sudo_command
        except Exception as e:
            print_status("FAIL", f"Error checking private key file: {e}")
    else:
        print_status("WARN", "Private Key File does not exist. (Skipping detailed permission check)")

    # --- Part 3: Sudo NOPASSWD Configuration ---
    print_header("Part 3: Sudo NOPASSWD Configuration")
    check_sudo_nopasswd("gitlab-ctl", GITLAB_CTL_PATH)
    check_sudo_nopasswd("chmod", CHMOD_PATH)

    # --- Part 4: acme.sh Environment ---
    print_header("Part 4: acme.sh Environment")
    print(f"  Checking if acme.sh home directory exists ({ACME_SH_HOME})... ", end='')
    if os.path.isdir(ACME_SH_HOME):
        print_status("OK", "Directory found.")
    else:
        print_status("FAIL", "Directory not found.")

    print(f"  Checking if acme.sh executable exists ({ACME_SH_HOME}/acme.sh)... ", end='')
    acme_sh_executable = os.path.join(ACME_SH_HOME, "acme.sh")
    if os.path.isfile(acme_sh_executable) and os.access(acme_sh_executable, os.X_OK):
        print_status("OK", "Executable found and is executable.")
    else:
        print_status("FAIL", "Executable not found or not executable.")

    print_header("Permissions Check Complete")
    print(f"Review {Colors.RED}FAIL{Colors.NC} or {Colors.YELLOW}WARN{Colors.NC} messages above and address them.")
    print(f"For certificate/key files, a {Colors.YELLOW}WARN{Colors.NC} might indicate they are temporarily writable by your group for acme.sh to update them,")
    print(f"but they should be secured to {Colors.GREEN}644/600 root:root{Colors.NC} immediately after deployment by the acme.sh reloadcmd.")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main()
