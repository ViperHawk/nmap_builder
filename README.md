# Interactive NMAP Command Builder

A comprehensive command-line tool for building NMAP scan commands interactively with educational features, command history, and execution capabilities.

**Author:** Ross Durrer  
**Created:** 2025  
**License:** MIT

## Features

### 🎯 **Interactive Command Building**
- Step-by-step guided interface for building NMAP commands
- Comprehensive explanations for each option
- Real-time command preview and breakdown
- Input validation and error handling

### 📚 **Educational Mode**
- Detailed explanations of NMAP options and techniques
- Command breakdown with parameter descriptions
- Built-in help system and documentation
- Perfect for learning network scanning concepts

### 🚀 **Quick Scan Templates**
- Pre-configured scan templates for common use cases
- Host discovery, stealth scanning, vulnerability assessment
- Web server scanning, UDP services, and more
- Customizable target specification

### 💾 **Command Management**
- Save commands as executable bash scripts
- Command history tracking (last 50 commands)
- Reuse previous commands with modifications
- Export and share scan configurations

### ⚡ **Execution & Output**
- Direct command execution from the tool
- Multiple output format support (Normal, XML, Greppable)
- Verbose logging and debugging options
- Integration with system clipboard

## Installation

### Prerequisites
- Python 3.6 or higher
- NMAP installed on your system

### Install NMAP
```bash
# Ubuntu/Debian
sudo apt-get install nmap

# CentOS/RHEL/Fedora
sudo yum install nmap
# or
sudo dnf install nmap

# macOS
brew install nmap

# Windows
# Download from https://nmap.org/download.html
```

### Install the Tool
```bash
# Clone or download the script
curl -O https://raw.githubusercontent.com/user/repo/main/nmap_builder.py

# Make executable
chmod +x nmap_builder.py

# Optional: Install clipboard support
pip install pyperclip
```

## Usage

### Basic Usage
```bash
python3 nmap_builder.py
```

### Command Line Options
```bash
python3 nmap_builder.py --help     # Show help
python3 nmap_builder.py --version  # Show version
```

## Scan Types Supported

| Scan Type | Flag | Description |
|-----------|------|-------------|
| TCP SYN Scan | `-sS` | Half-open scan, stealthy and fast |
| TCP Connect Scan | `-sT` | Full TCP connection, works without root |
| UDP Scan | `-sU` | Scan UDP ports (slower) |
| TCP ACK Scan | `-sA` | Firewall rule detection |
| TCP Window Scan | `-sW` | Window size exploitation |
| TCP Maimon Scan | `-sM` | FIN/ACK probe |
| TCP Null Scan | `-sN` | No flags set (stealth) |
| TCP FIN Scan | `-sF` | FIN flag only (stealth) |
| TCP Xmas Scan | `-sX` | FIN, PSH, URG flags (stealth) |
| Ping Scan | `-sn` | Host discovery only |
| List Scan | `-sL` | List targets without scanning |
| Version Detection | `-sV` | Service version detection |

## Port Specification Options

- **Default NMAP ports**: ~1000 most common ports
- **Fast scan** (`-F`): Top 100 ports
- **All ports** (`-p-`): All 65535 ports
- **Top N ports** (`--top-ports N`): Most common N ports
- **Port ranges** (`-p 1-1000`): Custom ranges
- **Port lists** (`-p 80,443,8080`): Specific ports
- **Predefined sets**: Web ports, database ports, remote access ports

## Target Format Examples

```bash
# Single IP
192.168.1.1

# IP Range
192.168.1.1-254

# CIDR Notation
192.168.1.0/24

# Hostname
example.com

# Multiple targets
192.168.1.1,192.168.1.2,example.com

# Input file
-iL targets.txt
```

## Quick Scan Templates

### 1. Host Discovery
```bash
nmap -sn 192.168.1.0/24
```
Fast ping scan to discover live hosts

### 2. Fast TCP Scan
```bash
nmap -F 192.168.1.1
```
Scan top 100 most common ports

### 3. Comprehensive Scan
```bash
nmap -sS -sV -O -A 192.168.1.1
```
SYN scan with version and OS detection

### 4. Stealth Scan
```bash
nmap -sS -T1 -f 192.168.1.1
```
Slow, fragmented SYN scan for IDS evasion

### 5. Vulnerability Scan
```bash
nmap -sV --script=vuln 192.168.1.1
```
Version detection with vulnerability scripts

### 6. Web Server Scan
```bash
nmap -p 80,443 -sV --script=http-* 192.168.1.1
```
Focus on web services with HTTP scripts

## Advanced Features

### Command History
- Automatically saves last 50 commands
- Stored in `~/.nmap_builder/command_history.json`
- Reuse and modify previous commands
- Timestamp tracking

### Script Generation
- Save commands as executable bash scripts
- Automatic script documentation
- Proper file permissions (`chmod +x`)
- Command breakdown in comments

### Output Formats
- **Normal** (`-oN`): Human-readable format
- **XML** (`-oX`): Structured XML output
- **Greppable** (`-oG`): Grep-friendly format
- **All formats** (`-oA`): Save in all formats
- **Script Kiddie** (`-oS`): Leet speak output

## Timing Templates

| Template | Flag | Description |
|----------|------|-------------|
| Paranoid | `-T0` | Very slow, IDS evasion |
| Sneaky | `-T1` | Slow, IDS evasion |
| Polite | `-T2` | Slow, less bandwidth |
| Normal | `-T3` | Default timing |
| Aggressive | `-T4` | Fast, assume fast network |
| Insane | `-T5` | Very fast, may miss results |

## Detection Options

### Service & Version Detection
- **Service Version** (`-sV`): Detect service versions
- **OS Detection** (`-O`): Enable OS detection
- **Aggressive Scan** (`-A`): Combined detection features

### NSE Script Categories
- **Default scripts** (`-sC`): Safe, common scripts
- **All scripts** (`--script=all`): All available scripts
- **Vulnerability** (`--script=vuln`): Vulnerability detection
- **Authentication** (`--script=auth`): Authentication testing
- **Discovery** (`--script=discovery`): Network discovery
- **Custom scripts** (`--script=script-name`): Specific scripts

## Security Considerations

### Ethical Use
- Only scan networks you own or have explicit permission to test
- Respect rate limits and avoid overwhelming target systems
- Follow responsible disclosure for any vulnerabilities found
- Comply with local laws and regulations

### Stealth Techniques
- Use timing templates (`-T0`, `-T1`) for slower, stealthier scans
- Fragment packets (`-f`) to evade simple packet filters
- Randomize target order (`--randomize-hosts`)
- Use decoy addresses (`-D`) to obscure scan source

## Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Run with sudo for SYN scans
sudo python3 nmap_builder.py
```

**NMAP Not Found**
```bash
# Check NMAP installation
which nmap
nmap --version

# Install if missing (see Installation section)
```

**Script Execution Fails**
```bash
# Make script executable
chmod +x generated_script.sh

# Check script permissions
ls -la generated_script.sh
```

### Performance Tips
- Use `-F` for quick scans during reconnaissance
- Combine `-T4` with `-F` for fast initial scans
- Use `--min-rate` and `--max-rate` for consistent timing
- Scan UDP ports separately due to slower performance

## File Structure

```
~/.nmap_builder/
├── command_history.json    # Command history storage
└── scripts/               # Generated bash scripts (optional)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- New scan templates
- Additional NSE script categories
- UI/UX improvements
- Bug fixes and optimizations
- Documentation improvements

## Changelog

### Version 1.0 (2025)
- Initial release
- Interactive command building
- Quick scan templates
- Command history tracking
- Script generation
- Educational mode

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational and authorized security testing purposes only. Users are responsible for complying with applicable laws and obtaining proper authorization before scanning any networks or systems.

## Support

For issues, questions, or feature requests, please open an issue on the project repository.

---

**Happy Scanning!** 🔍

*Remember: With great power comes great responsibility. Use this tool ethically and legally.*
