#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${NETWORK_CONFIG:-$PROJECT_ROOT/configs/network.env}"
SECRETS_FILE="${NETWORK_SECRETS:-$PROJECT_ROOT/configs/network.secrets.env}"
DRY_RUN=false

usage() {
  printf 'Usage: sudo %s [--dry-run]\n' "$(basename "$0")"
}

log() { printf '[network] %s\n' "$*"; }
die() { printf '[network] ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if [[ "$DRY_RUN" == true ]]; then
    printf '[dry-run]'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

for argument in "$@"; do
  case "$argument" in
    --dry-run) DRY_RUN=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; die "unknown argument: $argument" ;;
  esac
done

[[ "$(uname -s)" == Linux ]] || die 'this script supports Raspberry Pi/Linux only'
[[ "${EUID}" -eq 0 ]] || die 'run this deployment script with sudo'
command -v nmcli >/dev/null || die 'NetworkManager/nmcli is required; install it before running this script'
[[ -r "$CONFIG_FILE" ]] || die "missing network configuration: $CONFIG_FILE"
[[ -r "$SECRETS_FILE" ]] || die "missing network secrets file: $SECRETS_FILE"

# shellcheck disable=SC1090
source "$CONFIG_FILE"
# shellcheck disable=SC1090
source "$SECRETS_FILE"

: "${NETWORK_INTERFACE:?NETWORK_INTERFACE is required}"
: "${WIFI_INTERFACE:?WIFI_INTERFACE is required}"
: "${WIFI_SSID:?WIFI_SSID is required}"
: "${WIFI_PASSWORD:?WIFI_PASSWORD is required}"
: "${HOTSPOT_SSID:?HOTSPOT_SSID is required}"
: "${HOTSPOT_PASSWORD:?HOTSPOT_PASSWORD is required}"
: "${FALLBACK_ROBOT_ADDRESS:?FALLBACK_ROBOT_ADDRESS is required}"
: "${MEDIA_ROOT:?MEDIA_ROOT is required}"
: "${SMB_SHARE_NAME:?SMB_SHARE_NAME is required}"
: "${SMB_USER:?SMB_USER is required}"
: "${SMB_PASSWORD:?SMB_PASSWORD is required}"

[[ "$SECRETS_FILE" == "$PROJECT_ROOT"/* ]] || die 'secrets file must be within the Control project directory'
if [[ "$DRY_RUN" == false ]]; then
  permissions="$(stat -c '%a' "$SECRETS_FILE")"
  [[ "$permissions" == 600 || "$permissions" == 400 ]] || die "secrets file must have mode 600 or 400 (found $permissions)"
fi

nm_connection_exists() { nmcli -t -f NAME connection show | grep -Fxq "$1"; }

log "deploying network configuration from $CONFIG_FILE"
log "wired interface: $NETWORK_INTERFACE; Wi-Fi interface: $WIFI_INTERFACE"

if nm_connection_exists "$WIFI_CONNECTION_NAME"; then
  run nmcli connection modify "$WIFI_CONNECTION_NAME" connection.interface-name "$WIFI_INTERFACE" 802-11-wireless.ssid "$WIFI_SSID" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "$WIFI_PASSWORD" connection.autoconnect yes connection.autoconnect-retries 3
else
  run nmcli connection add type wifi ifname "$WIFI_INTERFACE" con-name "$WIFI_CONNECTION_NAME" ssid "$WIFI_SSID"
  run nmcli connection modify "$WIFI_CONNECTION_NAME" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "$WIFI_PASSWORD" connection.autoconnect yes connection.autoconnect-retries 3
fi

if nm_connection_exists "$HOTSPOT_CONNECTION_NAME"; then
  run nmcli connection modify "$HOTSPOT_CONNECTION_NAME" connection.interface-name "$WIFI_INTERFACE" 802-11-wireless.mode ap 802-11-wireless.ssid "$HOTSPOT_SSID" 802-11-wireless.channel "${HOTSPOT_CHANNEL:-6}" ipv4.method shared ipv4.addresses "$FALLBACK_ROBOT_ADDRESS" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "$HOTSPOT_PASSWORD" connection.autoconnect no
else
  run nmcli connection add type wifi ifname "$WIFI_INTERFACE" con-name "$HOTSPOT_CONNECTION_NAME" ssid "$HOTSPOT_SSID"
  run nmcli connection modify "$HOTSPOT_CONNECTION_NAME" 802-11-wireless.mode ap 802-11-wireless.channel "${HOTSPOT_CHANNEL:-6}" ipv4.method shared ipv4.addresses "$FALLBACK_ROBOT_ADDRESS" 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk "$HOTSPOT_PASSWORD" connection.autoconnect no
fi

if [[ "$DRY_RUN" == false ]]; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y avahi-daemon samba
  systemctl enable avahi-daemon
  systemctl restart avahi-daemon

  id "$SMB_USER" >/dev/null || die "SMB user does not exist: $SMB_USER"
  [[ -d "$MEDIA_ROOT" ]] || die "media directory does not exist: $MEDIA_ROOT"
  cp -a /etc/samba/smb.conf "/etc/samba/smb.conf.backup.$(date -u +%Y%m%dT%H%M%SZ)"
  cat > /etc/samba/smb.conf <<EOF
[global]
   workgroup = WORKGROUP
   server string = ${ROBOT_HOSTNAME:-robot}
   security = user
   map to guest = never
   interfaces = lo ${NETWORK_INTERFACE} ${WIFI_INTERFACE}
   bind interfaces only = yes
   min protocol = SMB2

[${SMB_SHARE_NAME}]
   path = ${MEDIA_ROOT}
   browseable = yes
   read only = no
   valid users = ${SMB_USER}
   force user = ${SMB_USER}
   create mask = 0640
   directory mask = 0750
EOF
  printf '%s\n' "$SMB_PASSWORD" | smbpasswd -s -a "$SMB_USER"
  smbpasswd -e "$SMB_USER"
  testparm -s >/dev/null
  systemctl enable smbd
  systemctl restart smbd
fi

if [[ -n "${ROBOT_HOSTNAME:-}" ]]; then
  run hostnamectl set-hostname "$ROBOT_HOSTNAME"
fi

if [[ "${WIRED_DHCP:-true}" == true ]]; then
  run nmcli connection modify "$NETWORK_INTERFACE" ipv4.method auto ipv4.addresses '' ipv4.gateway ''
else
  : "${WIRED_STATIC_ADDRESS:?WIRED_STATIC_ADDRESS is required when WIRED_DHCP=false}"
  run nmcli connection modify "$NETWORK_INTERFACE" ipv4.method manual ipv4.addresses "$WIRED_STATIC_ADDRESS" ipv4.gateway "${WIRED_GATEWAY:-}"
fi

run systemctl enable NetworkManager
run systemctl restart NetworkManager
log 'network profiles deployed; preferred Wi-Fi is configured to retry and hotspot is available for controlled failover'
log 'verify with: nmcli connection show; nmcli device status'
