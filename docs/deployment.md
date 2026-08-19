# Raspberry Pi deployment

The Control service is installed beside Cockpit and Datalogger on the robot. The current combined provisioning layout is `/home/pi/ROV---Control`.

## One-time installation

From the repository root on the target machine:

```bash
chmod +x scripts/*.sh
./scripts/1_install_dependencies.sh
```

On Windows use `scripts\\1_install_dependencies.bat`; it automatically downloads a project-local 64-bit WinPython runtime when needed and installs the shared `requirements.txt` with that runtime's `pip`. This includes Uvicorn and does not require `uv`. On macOS use the shell script without `sudo`; it automatically installs `uv`, creates `.venv`, and installs the same `requirements.txt`. On Linux/Raspberry Pi, use the Control deployment script for NetworkManager, NATS Core, Nginx, Samba, Avahi, and required system packages.

The Windows bootstrap is designed for machines where users do not have administrator rights: it installs below the project directory, rejects UNC paths for predictable process/filesystem behavior, and uses portable Python plus `pip` rather than requiring system Python or `uv`. It still needs write access to the project directory and network access for first-time downloads.

## Start the application

```bash
./scripts/2_start_app.sh
```

On Windows use `scripts\\2_start_app.bat`. On macOS, or on Linux without deployed systemd units, the shell script starts the local development service. On a deployed Raspberry Pi, use the systemd units and Control deployment scripts; restarting services may interrupt the ROV.

## Services

| Service | Unit/config | Role |
|---|---|---|
| NATS Core | `nats://127.0.0.1:4222` | Local service transport |
| Nginx | `Configs/nginx.conf` | HTTP reverse proxy and static files |
| Motion | `Configs/motion*.conf` | Camera streams |
| Python | `Configs/python.service` | Hardware control loop |
| Cockpit | `Configs/cockpit.service` | FastAPI/Uvicorn web application |

Camera inventory is stored in `Configs/cameras.json`. The Cockpit `/cameras/` page edits this inventory. Motion still uses its generated/deployed `.conf` files, so restart Motion after applying a matching configuration change.

Cockpit media is stored below `MEDIA_ROOT` (default: `<project>/media`), with `stills/`, `videos/`, and `data/csv/` subdirectories. On the Raspberry Pi, Motion writes recordings to `/home/pi/ROV---Cockpit/media/videos`. `MEDIA_MIN_FREE_GB` defaults to 2 GB; the oldest recordings are removed when the free-space floor is reached. The default recording segment length is 30 minutes and is stored in `configs/media.json`.

The Cockpit `/files/` page captures stills from the current Motion frame, displays the still gallery, lists recordings, and provides downloads. View-only access is anonymous. Driver/admin login and password management exist, but enforcement of control and every administrative route remains incomplete.

## Install/update

From the repository's `Configs` directory on the Pi:

```bash
sudo bash setup.sh
```

The script copies configuration files into system locations, reloads systemd, and enables/restarts the Python and Cockpit services. Review the script before running it on a new image because it assumes existing packages, users, paths, and permissions.

## First checks

```bash
systemctl status nats nginx cockpit
curl http://127.0.0.1/
curl http://127.0.0.1:8080/json/
nats sub '>'
```

NATS is currently configured for local robot services. Review authentication before exposing it beyond the trusted robot network.
## Linux/Raspberry Pi deployment

From the repository root, run `scripts/1_install_dependencies.sh` as the normal runtime user, then use `scripts/2_start_app.sh`. Control requires NATS Core at `NATS_URL` before it can start safely.
# Network deployment

Control owns the Raspberry Pi network deployment. The supported initial implementation uses NetworkManager and `scripts/0_deploy_network.sh` to configure a wired interface, a preferred Wi-Fi client connection, and a fallback Wi-Fi hotspot. The script is intended for Raspberry Pi/Linux only and must be reviewed before use on a robot.

Copy `configs/network.env.example` to `configs/network.env` and `configs/network.secrets.example` to `configs/network.secrets.env`. Development test credentials may be versioned for easy relocation; before robot or shared-network use, regenerate them and put the real values in the ignored secrets file, then protect it with mode `600`:

```bash
cp configs/network.env.example configs/network.env
cp configs/network.secrets.example configs/network.secrets.env
chmod 600 configs/network.secrets.env
sudo scripts/0_deploy_network.sh --dry-run
sudo scripts/0_deploy_network.sh
```

The script configures one preferred Wi-Fi client profile and one non-autoconnect hotspot profile. The fallback network is `192.168.42.0/24`, with the robot at `192.168.42.1` and clients in `192.168.42.100` to `192.168.42.200`. The `.42` choice is intentional: it references *The Hitchhiker's Guide to the Galaxy* and was selected because this private range is not used elsewhere in the current environment. It remains a convention rather than a requirement; deployments must avoid conflicts with networks they join. Wi-Fi failover policy and health monitoring remain Control runtime responsibilities; the deployment script does not claim that physical failover has been validated. Wired DHCP is enabled by default, with an optional static address. Only one default gateway should be configured.

The deployment also installs Avahi and Samba. Avahi advertises the configured hostname and local services. Samba configuration is intended to expose the Cockpit media directory as an authenticated `media` share with read and delete access; the share must be configured only after the media path and account have been reviewed. Do not enable guest access or expose the share outside trusted robot networks.
