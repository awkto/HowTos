#!/bin/bash

# acme.sh GitLab SSL Permission Checker
# This script checks the necessary file and directory permissions for acme.sh to
# manage GitLab SSL certificates in an Omnibus installation.
# Run this script as the user configured to run acme.sh (e.g., 'altanc' or 'user').

# --- Color Codes ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Configuration ---
ACME_SH_USER="$(whoami)"
ACME_SH_HOME="/home/${ACME_SH_USER}/.acme.sh"
GITLAB_SSL_DIR="/etc/gitlab/ssl"
GITLAB_RB_PATH="/etc/gitlab/gitlab.rb"
SSLADMINS_GROUP="ssladmins"
GITLAB_CTL_PATH="/usr/bin/gitlab-ctl" # Common path, verify with 'which gitlab-ctl'
CHMOD_PATH="/bin/chmod" # Common path, verify with 'which chmod'

# --- Helper Functions ---
print_header() {
    echo -e "${BLUE}--- $1 ---${NC}"
}

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        "OK") echo -e "  ${GREEN}✓ OK${NC}: $message" ;;
        "FAIL") echo -e "  ${RED}✗ FAIL${NC}: $message" ;;
        "WARN") echo -e "  ${YELLOW}! WARN${NC}: $message" ;;
    esac
}

check_command() {
    local cmd="$1"
    local desc="$2"
    echo -n "  Checking if '$cmd' is available... "
    if command -v "$cmd" >/dev/null 2>&1; then
        print_status "OK" "$desc available."
        return 0
    else
        print_status "FAIL" "$desc not found. (Command '$cmd' not in PATH)"
        return 1
    fi
}

check_user_in_group() {
    local user="$1"
    local group="$2"
    echo -n "  Checking if user '$user' is in group '$group'... "
    if id -Gn "$user" | grep -qw "$group"; then
        print_status "OK" "User '$user' is in group '$group'."
        return 0
    else
        print_status "FAIL" "User '$user' is NOT in group '$group'."
        return 1
    fi
}

check_file_permissions() {
    local file_path="$1"
    local expected_perms="$2"
    local expected_owner="$3"
    local expected_group="$4"
    local file_type="$5" # e.g., "Private Key", "Certificate", "Directory"

    echo -n "  Checking $file_type permissions for $file_path... "
    if [ ! -e "$file_path" ]; then
        print_status "WARN" "$file_type does not exist. (Skipping detailed permission check)"
        return 0
    fi

    # Use sudo to get accurate permissions for root-owned files
    local perms=$(sudo stat -c "%a" "$file_path" 2>/dev/null)
    local owner=$(sudo stat -c "%U" "$file_path" 2>/dev/null)
    local group=$(sudo stat -c "%G" "$file_path" 2>/dev/null)

    if [ -z "$perms" ]; then
        print_status "FAIL" "Could not get permissions for $file_path. (Check sudo permissions for stat)"
        return 1
    fi

    local status="OK"
    local issues=()

    if [ "$perms" != "$expected_perms" ]; then
        issues+=("Permissions: Current=${perms}, Expected=${expected_perms}")
        status="FAIL"
    fi
    if [ "$owner" != "$expected_owner" ]; then
        issues+=("Owner: Current=${owner}, Expected=${expected_owner}")
        status="FAIL"
    fi
    if [ "$group" != "$expected_group" ]; then
        issues+=("Group: Current=${group}, Expected=${expected_group}")
        status="FAIL"
    fi

    if [ "$status" == "OK" ]; then
        print_status "OK" "Perms: ${perms}, Owner: ${owner}, Group: ${group}"
        return 0
    else
        print_status "FAIL" "Perms: ${perms}, Owner: ${owner}, Group: ${group}"
        for issue in "${issues[@]}"; do
            echo -e "    - ${RED}$issue${NC}"
        done
        return 1
    fi
}

check_sudo_nopasswd() {
    local cmd_name="$1"
    local cmd_path="$2"
    echo -n "  Checking sudo NOPASSWD for '$cmd_name' ($cmd_path)... "
    # Try to execute a command that will fail harmlessly, but will tell us if sudo works NOPASSWD
    # Using -v for gitlab-ctl is usually safe. For chmod, --help is safe.
    if sudo -n "$cmd_path" -v >/dev/null 2>&1 || sudo -n "$cmd_path" --help >/dev/null 2>&1; then
        print_status "OK" "NOPASSWD for '$cmd_name' is configured."
        return 0
    else
        print_status "FAIL" "NOPASSWD for '$cmd_name' is NOT configured. (Password likely required or command path incorrect. Check sudoers.)"
        return 1
    fi
}

# --- Main Script Logic ---

print_header "acme.sh GitLab SSL Permission Checker"
echo "Running as user: ${ACME_SH_USER}"
echo "--------------------------------------------------------"

# 1. Dynamically get Gitlab FQDN and SSL file paths from gitlab.rb
if [ ! -f "$GITLAB_RB_PATH" ]; then
    echo -e "${RED}Error: ${GITLAB_RB_PATH} not found. Cannot determine GitLab SSL configuration.${NC}"
    echo "Please ensure GitLab Omnibus is installed or provide the correct path to gitlab.rb."
    exit 1
fi

echo -e "${BLUE}Parsing ${GITLAB_RB_PATH} for SSL configuration...${NC}"
# Extract FQDN, certificate path, and key path from gitlab.rb
# Using sudo to read gitlab.rb as it might be root-readable only
# Refined parsing using 'cut' and 'tr' to handle various quote types and whitespace
GITLAB_FQDN=$(sudo grep -E "^[[:space:]]*external_url" "$GITLAB_RB_PATH" 2>/dev/null | \
              cut -d"'" -f2 | cut -d'"' -f2 | sed -E 's|^https?://||' | sed 's|/.*||' | head -n 1)

GITLAB_CERT_FILE=$(sudo grep -E "^[[:space:]]*nginx\['ssl_certificate'\]" "$GITLAB_RB_PATH" 2>/dev/null | \
                   sed -E "s/^[[:space:]]*nginx\['ssl_certificate'\][[:space:]]*=[[:space:]]*['\"]?([^'\"]*)['\"]?.*/\1/" | head -n 1)

GITLAB_KEY_FILE=$(sudo grep -E "^[[:space:]]*nginx\['ssl_certificate_key'\]" "$GITLAB_RB_PATH" 2>/dev/null | \
                  sed -E "s/^[[:space:]]*nginx\['ssl_certificate_key'\][[:space:]]*=[[:space:]]*['\"]?([^'\"]*)['\"]?.*/\1/" | head -n 1)


# Fallback/validation for FQDN if parsing fails or is incomplete
if [ -z "$GITLAB_FQDN" ]; then
    echo -e "${YELLOW}Warning: Could not automatically detect GitLab FQDN from ${GITLAB_RB_PATH}.${NC}"
    read -rp "Please manually enter your GitLab FQDN (e.g., gitlab.example.com): " GITLAB_FQDN_MANUAL
    if [ -z "$GITLAB_FQDN_MANUAL" ]; then
        echo -e "${RED}Error: GitLab FQDN is required. Exiting.${NC}"
        exit 1
    fi
    GITLAB_FQDN="$GITLAB_FQDN_MANUAL"
fi

# Fallback/validation for cert/key paths
if [ -z "$GITLAB_CERT_FILE" ]; then
    echo -e "${YELLOW}Warning: Could not automatically detect SSL certificate path from ${GITLAB_RB_PATH}. Assuming ${GITLAB_SSL_DIR}/${GITLAB_FQDN}.cer${NC}"
    GITLAB_CERT_FILE="${GITLAB_SSL_DIR}/${GITLAB_FQDN}.cer"
fi
if [ -z "$GITLAB_KEY_FILE" ]; then
    echo -e "${YELLOW}Warning: Could not automatically detect SSL key path from ${GITLAB_RB_PATH}. Assuming ${GITLAB_SSL_DIR}/${GITLAB_FQDN}.key${NC}"
    GITLAB_KEY_FILE="${GITLAB_SSL_DIR}/${GITLAB_FQDN}.key"
fi


echo -e "Using GitLab FQDN: ${BLUE}${GITLAB_FQDN}${NC}"
echo -e "GitLab Certificate File: ${BLUE}${GITLAB_CERT_FILE}${NC}"
echo -e "GitLab Key File: ${BLUE}${GITLAB_KEY_FILE}${NC}"
echo "--------------------------------------------------------"

print_header "Part 1: User and Group Permissions"
check_user_in_group "${ACME_SH_USER}" "${SSLADMINS_GROUP}"

echo ""
print_header "Part 2: Directory and File Permissions for GitLab SSL"
check_file_permissions "${GITLAB_SSL_DIR}" "770" "root" "${SSLADMINS_GROUP}" "GitLab SSL Directory"

# Certificate File Check: Expect 644 root root, but allow 664 root ssladmins if still in transition
echo -n "  Checking Certificate File (${GITLAB_CERT_FILE})... "
if [ -e "$GITLAB_CERT_FILE" ]; then
    CERT_PERMS=$(sudo stat -c "%a" "$GITLAB_CERT_FILE" 2>/dev/null)
    CERT_OWNER=$(sudo stat -c "%U" "$GITLAB_CERT_FILE" 2>/dev/null)
    CERT_GROUP=$(sudo stat -c "%G" "$GITLAB_CERT_FILE" 2>/dev/null)

    if [ "$CERT_PERMS" == "644" ] && [ "$CERT_OWNER" == "root" ] && [ "$CERT_GROUP" == "root" ]; then
        print_status "OK" "Perms: ${CERT_PERMS}, Owner: ${CERT_OWNER}, Group: ${CERT_GROUP} (Secure)"
    elif [ "$CERT_PERMS" == "664" ] && [ "$CERT_OWNER" == "root" ] && [ "$CERT_GROUP" == "${SSLADMINS_GROUP}" ]; then
        print_status "WARN" "Perms: ${CERT_PERMS}, Owner: ${CERT_OWNER}, Group: ${CERT_GROUP} (Writable by ${SSLADMINS_GROUP} for acme.sh, should be secured to 644 root root by reloadcmd)"
    else
        print_status "FAIL" "Perms: ${CERT_PERMS}, Owner: ${CERT_OWNER}, Group: ${CERT_GROUP}"
        echo -e "    - ${RED}Expected 644 root root, or 664 root ${SSLADMINS_GROUP} during deployment.${NC}"
    fi
else
    print_status "WARN" "Certificate File does not exist. (Skipping detailed permission check)"
fi

# Private Key File Check: Expect 600 root root, but allow 660 root ssladmins if still in transition
echo -n "  Checking Private Key File (${GITLAB_KEY_FILE})... "
if [ -e "$GITLAB_KEY_FILE" ]; then
    KEY_PERMS=$(sudo stat -c "%a" "$GITLAB_KEY_FILE" 2>/dev/null)
    KEY_OWNER=$(sudo stat -c "%U" "$GITLAB_KEY_FILE" 2>/dev/null)
    KEY_GROUP=$(sudo stat -c "%G" "$GITLAB_KEY_FILE" 2>/dev/null)

    if [ "$KEY_PERMS" == "600" ] && [ "$KEY_OWNER" == "root" ] && [ "$KEY_GROUP" == "root" ]; then
        print_status "OK" "Perms: ${KEY_PERMS}, Owner: ${KEY_OWNER}, Group: ${KEY_GROUP} (Secure)"
    elif [ "$KEY_PERMS" == "660" ] && [ "$KEY_OWNER" == "root" ] && [ "$KEY_GROUP" == "${SSLADMINS_GROUP}" ]; then
        print_status "WARN" "Perms: ${KEY_PERMS}, Owner: ${KEY_OWNER}, Group: ${KEY_GROUP} (Writable by ${SSLADMINS_GROUP} for acme.sh, should be secured to 600 root root by reloadcmd)"
    else
        print_status "FAIL" "Perms: ${KEY_PERMS}, Owner: ${KEY_OWNER}, Group: ${KEY_GROUP}"
        echo -e "    - ${RED}Expected 600 root root, or 660 root ${SSLADMINS_GROUP} during deployment.${NC}"
    fi
else
    print_status "WARN" "Private Key File does not exist. (Skipping detailed permission check)"
fi


echo ""
print_header "Part 3: Sudo NOPASSWD Configuration"
check_sudo_nopasswd "gitlab-ctl" "$GITLAB_CTL_PATH"
check_sudo_nopasswd "chmod" "$CHMOD_PATH"

echo ""
print_header "Part 4: acme.sh Environment"
echo -n "  Checking if acme.sh home directory exists (${ACME_SH_HOME})... "
if [ -d "$ACME_SH_HOME" ]; then
    print_status "OK" "Directory found."
else
    print_status "FAIL" "Directory not found."
fi

echo -n "  Checking if acme.sh executable exists (${ACME_SH_HOME}/acme.sh)... "
if [ -f "$ACME_SH_HOME/acme.sh" ] && [ -x "$ACME_SH_HOME/acme.sh" ]; then
    print_status "OK" "Executable found and is executable."
else
    print_status "FAIL" "Executable not found or not executable."
fi

echo ""
print_header "Permissions Check Complete"
echo -e "Review ${RED}FAIL${NC} or ${YELLOW}WARN${NC} messages above and address them."
echo -e "For certificate/key files, a ${YELLOW}WARN${NC} might indicate they are temporarily writable by your group for acme.sh to update them,"
echo -e "but they should be secured to ${GREEN}644/600 root:root${NC} immediately after deployment by the acme.sh reloadcmd."
echo "--------------------------------------------------------"
