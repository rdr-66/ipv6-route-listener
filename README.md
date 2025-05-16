# 🧭 Route Listener for ICMPv6 RAs (Thread Border Routers)

This project listens for IPv6 Router Advertisements (RAs) from Thread Border Routers and automatically configures ULA prefixes and routes on the host system. It's specifically designed for environments like Synology DSM where the kernel is missing support for processing IPv6 route advertisements for Matter/Thread subnets.

## 🎯 Purpose

This tool was created to solve a specific problem when running Home Assistant on a Synology NAS:

1. The Synology DSM kernel is missing the `CONFIG_IPV6_ROUTE_INFO` kernel option
2. This prevents the system from automatically processing IPv6 Router Advertisements for subnets
3. Matter/Thread devices use these subnets for communication
4. Without proper routing, Home Assistant cannot communicate with Matter devices

This project provides a workaround by:
- Listening for ICMPv6 Router Advertisements
- Extracting ULA prefixes and routes
- Manually configuring these routes in the kernel using the `ip` command

## 🚀 Quick Start (with Docker)

1. **Clone this repo:**

    ```bash
    git clone https://github.com/your/repo.git
    cd route-listener
    ```

2. **Build and run the Docker container:**

    ```bash
    # Use default interface (eth0)
    ./run.sh

    # Or specify a custom interface
    ./run.sh -i wlan0

    # Enable verbose logging
    ./run.sh --verbose
    ```

## 🐍 Local Development

If you're not using Docker:

1. **Install Poetry:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. **Install dependencies:**

    ```bash
    poetry install
    ```

3. **Run the script:**

    ```bash
    # Use default interface (eth0)
    poetry run route-listen

    # Or specify a custom interface
    poetry run route-listen -i wlan0

    # Enable debug logging
    poetry run route-listen -i wlan0 --debug

    # Enable verbose logging
    poetry run route-listen --verbose
    ```

    Note: Since this tool needs to capture network packets, you might need to run it with sudo:

    ```bash
    sudo poetry run route-listen -i wlan0 --debug
    ```

    Available options:
    - `-i, --interface`: Specify the network interface to listen on (default: eth0)
    - `--debug`: Enable detailed debug logging
    - `--verbose`: Enable verbose logging output
    - `--enable-rs`: Enable Router Solicitation

## 💡 How It Works

1. **Route Detection:**
   - Listens for ICMPv6 Router Advertisements on the specified network interface
   - Extracts ULA prefixes and routes from the advertisements
   - Each route is processed only once (subsequent advertisements for the same route are ignored)
   - If multiple routes are advertised for the same subnet, the last route wins

2. **Route Filtering:**
   - Only ULA prefixes (starting with 'fd') are configured
   - Non-ULA prefixes are ignored by default
   - You can enable logging of ignored routes with the `--log-ignored` option
   - **Why only ULA prefixes?** Matter/Thread devices use ULA (Unique Local Address) prefixes for their internal communication. These prefixes are guaranteed to be unique and are not routable on the public internet, making them ideal for local network communication. By filtering for only ULA prefixes, we ensure we're only configuring routes that are relevant for Matter/Thread device communication.

3. **Route Configuration:**
   - When a new ULA route is detected, an external script (`thread-route.sh`) is called
   - The script uses the `ip` command to add the route to the kernel
   - Existing routes with the same prefix are removed before adding the new one
   - If multiple routes are advertised for the same subnet, the last route wins

4. **Interface Configuration:**
   - By default, the script listens on the `eth0` interface
   - You can specify a different interface using the `-i` option
   - The script will abort if the specified interface doesn't exist

## 📋 Example Output

```
[2023-04-19 10:15:30] 🚀 Starting ICMPv6 RA listener...
[2023-04-19 10:15:30] 📡 Listening for Router Advertisements on interface 'eth0'...
[2023-04-19 10:15:35] 🔔 Router Advertisement from fe80::1234:5678:9abc:def0
[2023-04-19 10:15:35]   📡 Prefix: fd00:1234:5678::/64
[2023-04-19 10:15:35]   🔧 Configuring new route: fd00:1234:5678::/64 via fe80::1234:5678:9abc:def0
[2023-04-19 10:15:35]   ✅ Route configuration output:
[2023-04-19 10:15:35]   🔍 Configuring route: fd00:1234:5678::/64 via fe80::1234:5678:9abc:def0 on interface eth0
[2023-04-19 10:15:35]   ➕ Adding route to fd00:1234:5678::/64 via fe80::1234:5678:9abc:def0 on eth0
[2023-04-19 10:15:35]   ✅ Added
[2023-04-19 10:15:40] 🔔 Router Advertisement from fe80::1234:5678:9abc:def0
[2023-04-19 10:15:40]   📡 Prefix: 2001:db8::/64
[2023-04-19 10:15:40]   ⏭️  Ignoring non-ULA prefix: 2001:db8::/64 via fe80::1234:5678:9abc:def0
[2023-04-19 10:15:40]   ℹ️  Only ULA prefixes (starting with 'fd') are configured for Matter/Thread device communication
[2023-04-19 10:15:40]   ℹ️  ULA prefixes are used for local network communication and are not routable on the public internet
[2023-04-19 10:15:45] 🔔 Router Advertisement from fe80::1234:5678:9abc:def0
[2023-04-19 10:15:45]   📡 Prefix: fd00:1234:5678::/64
[2023-04-19 10:15:45]   ⏭️  Route already configured: fd00:1234:5678::/64 via fe80::1234:5678:9abc:def0
[2023-04-19 10:15:50] 🔔 Router Advertisement from fe80::5678:9abc:def0:1234
[2023-04-19 10:15:50]   📡 Prefix: fd00:1234:5678::/64
[2023-04-19 10:15:50]   🔄 Updating route: fd00:1234:5678::/64 via fe80::5678:9abc:def0:1234 (previous: fe80::1234:5678:9abc:def0)
[2023-04-19 10:15:50]   ✅ Route configuration output:
[2023-04-19 10:15:50]   🔍 Configuring route: fd00:1234:5678::/64 via fe80::5678:9abc:def0:1234 on interface eth0
[2023-04-19 10:15:50]   ➕ Adding route to fd00:1234:5678::/64 via fe80::5678:9abc:def0:1234 on eth0
[2023-04-19 10:15:50]   ✅ Added
```

## 📜 History

This project was inspired by the discussion in the Home Assistant community about running Matter/Thread devices on a Synology NAS. The Synology DSM kernel is missing the `CONFIG_IPV6_ROUTE_INFO` kernel option, which prevents it from automatically processing IPv6 Router Advertisements for subnets that Matter devices use for communication.

This tool provides a workaround by manually configuring the routes based on the Router Advertisements, allowing Home Assistant to communicate with Matter devices on the Synology NAS.

## 🔗 References

- [Matter Server Docker Container on Synology NAS / Home Assistant Core](https://community.home-assistant.io/t/matter-server-docker-container-on-synology-nas-home-assistant-core/751120/15)

## Verification Tools

This project includes several tools to ensure code quality and consistency:

### Prerequisites

Before running any verification tools, make sure you have installed the project dependencies:

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### Makefile

The project includes a Makefile with targets for verification:

```bash
# Run all verification steps (format, lint, test, type-check)
make verify

# Run verification in check-only mode (for CI)
make verify-check

# Run individual steps
make format
make lint
make test
make type-check
```

### Verification Script

A simple script is provided to run the Makefile commands:

```bash
# Run verification in fix mode (for local development)
./scripts/verify.sh

# Run verification in check-only mode (for CI)
./scripts/verify.sh --check
```

### Pre-commit Hooks

Pre-commit hooks automatically run verification steps when you commit changes:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. (Optional) Run hooks on all files:
   ```bash
   pre-commit run --all-files
   ```

### GitHub Actions

The project includes a GitHub Actions workflow that runs verification on:
- Every push to the main branch
- Every pull request to the main branch

This ensures that all code in the repository meets quality standards.
