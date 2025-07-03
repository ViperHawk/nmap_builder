#!/usr/bin/env python3
"""
Interactive NMAP Command Builder
Author: Ross Durrer
Created: 2025

A command-line tool for building NMAP scan commands interactively.
Supports learning mode, command saving, and flexible output options.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class NmapBuilder:
    def __init__(self):
        self.command_parts = {
            'scan_type': '',
            'target': '',
            'ports': '',
            'timing': '',
            'detection': '',
            'output': '',
            'misc_options': []
        }
        
        self.scan_types = {
            '1': {'name': 'TCP SYN Scan', 'flag': '-sS', 'description': 'Half-open scan, stealthy and fast'},
            '2': {'name': 'TCP Connect Scan', 'flag': '-sT', 'description': 'Full TCP connection, works without root'},
            '3': {'name': 'UDP Scan', 'flag': '-sU', 'description': 'Scan UDP ports (slower)'},
            '4': {'name': 'TCP ACK Scan', 'flag': '-sA', 'description': 'Firewall rule detection'},
            '5': {'name': 'TCP Window Scan', 'flag': '-sW', 'description': 'Window size exploitation'},
            '6': {'name': 'TCP Maimon Scan', 'flag': '-sM', 'description': 'FIN/ACK probe'},
            '7': {'name': 'TCP Null Scan', 'flag': '-sN', 'description': 'No flags set (stealth)'},
            '8': {'name': 'TCP FIN Scan', 'flag': '-sF', 'description': 'FIN flag only (stealth)'},
            '9': {'name': 'TCP Xmas Scan', 'flag': '-sX', 'description': 'FIN, PSH, URG flags (stealth)'},
            '10': {'name': 'Ping Scan', 'flag': '-sn', 'description': 'Host discovery only'},
            '11': {'name': 'List Scan', 'flag': '-sL', 'description': 'List targets without scanning'},
            '12': {'name': 'Version Detection', 'flag': '-sV', 'description': 'Service version detection'}
        }
        
        self.timing_templates = {
            '0': {'name': 'Paranoid', 'flag': '-T0', 'description': 'Very slow, IDS evasion'},
            '1': {'name': 'Sneaky', 'flag': '-T1', 'description': 'Slow, IDS evasion'},
            '2': {'name': 'Polite', 'flag': '-T2', 'description': 'Slow, less bandwidth'},
            '3': {'name': 'Normal', 'flag': '-T3', 'description': 'Default timing'},
            '4': {'name': 'Aggressive', 'flag': '-T4', 'description': 'Fast, assume fast network'},
            '5': {'name': 'Insane', 'flag': '-T5', 'description': 'Very fast, may miss results'}
        }
        
        self.output_formats = {
            '1': {'name': 'Normal Output', 'flag': '-oN', 'ext': '.nmap'},
            '2': {'name': 'XML Output', 'flag': '-oX', 'ext': '.xml'},
            '3': {'name': 'Greppable Output', 'flag': '-oG', 'ext': '.gnmap'},
            '4': {'name': 'All Formats', 'flag': '-oA', 'ext': ''},
            '5': {'name': 'Script Kiddie', 'flag': '-oS', 'ext': '.skid'}
        }
        
        self.detection_options = {
            '1': {'name': 'Service Version Detection', 'flag': '-sV', 'description': 'Detect service versions'},
            '2': {'name': 'OS Detection', 'flag': '-O', 'description': 'Enable OS detection'},
            '3': {'name': 'Script Scan (Default)', 'flag': '-sC', 'description': 'Run default NSE scripts'},
            '4': {'name': 'Script Scan (All)', 'flag': '--script=all', 'description': 'Run all NSE scripts'},
            '5': {'name': 'Script Scan (Vuln)', 'flag': '--script=vuln', 'description': 'Run vulnerability scripts'},
            '6': {'name': 'Script Scan (Auth)', 'flag': '--script=auth', 'description': 'Run authentication scripts'},
            '7': {'name': 'Script Scan (Discovery)', 'flag': '--script=discovery', 'description': 'Run discovery scripts'},
            '8': {'name': 'Aggressive Scan', 'flag': '-A', 'description': 'Enable OS detection, version detection, script scanning'},
            '9': {'name': 'Custom Script', 'flag': '--script=', 'description': 'Specify custom NSE script'}
        }

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                 Interactive NMAP Command Builder             ║
║                        Author: Ross Durrer                   ║
║                         Created: 2025                        ║
╠══════════════════════════════════════════════════════════════╣
║  Build NMAP commands interactively with learning support    ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)

    def check_nmap_installed(self):
        """Check if NMAP is installed on the system"""
        try:
            result = subprocess.run(['nmap', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✓ NMAP detected: {version_line}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("✗ NMAP not found. Please install NMAP to use this tool.")
        print("  Ubuntu/Debian: sudo apt-get install nmap")
        print("  CentOS/RHEL: sudo yum install nmap")
        print("  macOS: brew install nmap")
        return False

    def get_scan_type(self):
        """Interactive scan type selection"""
        print("\n" + "="*60)
        print("STEP 1: SELECT SCAN TYPE")
        print("="*60)
        
        for key, value in self.scan_types.items():
            print(f"{key:2}. {value['name']:20} ({value['flag']:4}) - {value['description']}")
        
        while True:
            choice = input("\nSelect scan type [1-12]: ").strip()
            if choice in self.scan_types:
                selected = self.scan_types[choice]
                self.command_parts['scan_type'] = selected['flag']
                print(f"✓ Selected: {selected['name']} ({selected['flag']})")
                return
            print("Invalid choice. Please select 1-12.")

    def get_target(self):
        """Get target specification"""
        print("\n" + "="*60)
        print("STEP 2: SPECIFY TARGET(S)")
        print("="*60)
        print("Examples:")
        print("  Single IP:      192.168.1.1")
        print("  IP Range:       192.168.1.1-254")
        print("  CIDR:           192.168.1.0/24")
        print("  Hostname:       example.com")
        print("  Multiple:       192.168.1.1,192.168.1.2,example.com")
        print("  Input file:     -iL targets.txt")
        
        while True:
            target = input("\nEnter target(s): ").strip()
            if target:
                self.command_parts['target'] = target
                print(f"✓ Target set: {target}")
                return
            print("Target cannot be empty.")

    def get_port_specification(self):
        """Get port range specification"""
        print("\n" + "="*60)
        print("STEP 3: PORT SPECIFICATION (Optional)")
        print("="*60)
        
        port_options = {
            '1': {'name': 'Default NMAP ports', 'flag': '', 'description': 'NMAP default port selection (~1000 ports)'},
            '2': {'name': 'Fast scan', 'flag': '-F', 'description': 'Top 100 most common ports'},
            '3': {'name': 'All ports', 'flag': '-p-', 'description': 'All 65535 ports (very slow)'},
            '4': {'name': 'Top 100 ports', 'flag': '--top-ports 100', 'description': 'Most common 100 ports'},
            '5': {'name': 'Top 1000 ports', 'flag': '--top-ports 1000', 'description': 'Most common 1000 ports'},
            '6': {'name': 'Well-known ports', 'flag': '-p 1-1023', 'description': 'System/well-known ports (1-1023)'},
            '7': {'name': 'Common web ports', 'flag': '-p 80,443,8080,8443,8000,8888', 'description': 'HTTP/HTTPS and common web ports'},
            '8': {'name': 'Common service ports', 'flag': '-p 21,22,23,25,53,80,110,143,443,993,995', 'description': 'FTP, SSH, Telnet, SMTP, DNS, HTTP, POP, IMAP, HTTPS'},
            '9': {'name': 'Database ports', 'flag': '-p 1433,1521,3306,5432,27017', 'description': 'MSSQL, Oracle, MySQL, PostgreSQL, MongoDB'},
            '10': {'name': 'Remote access ports', 'flag': '-p 22,23,3389,5900,5901,5902', 'description': 'SSH, Telnet, RDP, VNC'},
            '11': {'name': 'Custom port range', 'flag': 'custom_range', 'description': 'Specify your own port range'},
            '12': {'name': 'Custom port list', 'flag': 'custom_list', 'description': 'Specify individual ports'},
            '13': {'name': 'Single port', 'flag': 'custom_single', 'description': 'Specify a single port'}
        }
        
        for key, value in port_options.items():
            print(f"{key:2}. {value['name']:20} ({value['flag'] if value['flag'] and not value['flag'].startswith('custom') else 'Custom':15}) - {value['description']}")
        
        while True:
            choice = input("\nSelect port specification [1-13]: ").strip()
            
            if choice in port_options:
                selected = port_options[choice]
                
                if selected['flag'] == 'custom_range':
                    # Custom port range
                    while True:
                        start_port = input("Enter starting port (1-65535): ").strip()
                        end_port = input("Enter ending port (1-65535): ").strip()
                        
                        try:
                            start = int(start_port)
                            end = int(end_port)
                            if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
                                ports_flag = f"-p {start}-{end}"
                                self.command_parts['ports'] = ports_flag
                                print(f"✓ Custom range set: {ports_flag}")
                                return
                            else:
                                print("Invalid range. Start and end must be 1-65535, and start <= end.")
                        except ValueError:
                            print("Please enter valid numbers.")
                
                elif selected['flag'] == 'custom_list':
                    # Custom port list
                    while True:
                        port_list = input("Enter ports separated by commas (e.g., 80,443,8080): ").strip()
                        if port_list:
                            try:
                                # Validate each port
                                ports = [int(p.strip()) for p in port_list.split(',')]
                                if all(1 <= p <= 65535 for p in ports):
                                    ports_flag = f"-p {port_list}"
                                    self.command_parts['ports'] = ports_flag
                                    print(f"✓ Custom ports set: {ports_flag}")
                                    return
                                else:
                                    print("All ports must be between 1 and 65535.")
                            except ValueError:
                                print("Please enter valid port numbers separated by commas.")
                        else:
                            print("Port list cannot be empty.")
                
                elif selected['flag'] == 'custom_single':
                    # Single custom port
                    while True:
                        single_port = input("Enter port number (1-65535): ").strip()
                        try:
                            port = int(single_port)
                            if 1 <= port <= 65535:
                                ports_flag = f"-p {port}"
                                self.command_parts['ports'] = ports_flag
                                print(f"✓ Single port set: {ports_flag}")
                                return
                            else:
                                print("Port must be between 1 and 65535.")
                        except ValueError:
                            print("Please enter a valid port number.")
                
                else:
                    # Predefined option
                    if selected['flag']:
                        self.command_parts['ports'] = selected['flag']
                        print(f"✓ Selected: {selected['name']} ({selected['flag']})")
                    else:
                        print(f"✓ Selected: {selected['name']} (using NMAP defaults)")
                    return
            
            print("Invalid choice. Please select 1-13.")

    def get_timing_template(self):
        """Get timing template"""
        print("\n" + "="*60)
        print("STEP 4: TIMING TEMPLATE (Optional)")
        print("="*60)
        
        for key, value in self.timing_templates.items():
            print(f"{key}. {value['name']:10} ({value['flag']:4}) - {value['description']}")
        
        choice = input("\nSelect timing template (0-5, or Enter for default): ").strip()
        if choice in self.timing_templates:
            selected = self.timing_templates[choice]
            self.command_parts['timing'] = selected['flag']
            print(f"✓ Selected: {selected['name']} ({selected['flag']})")
        else:
            print("✓ Using default timing")

    def get_detection_options(self):
        """Get detection and scripting options"""
        print("\n" + "="*60)
        print("STEP 5: DETECTION OPTIONS (Optional)")
        print("="*60)
        
        for key, value in self.detection_options.items():
            print(f"{key}. {value['name']:25} ({value['flag']:15}) - {value['description']}")
        
        print("\nSelect detection options (comma-separated, e.g., 1,2,3 or Enter for none):")
        choices = input("Your choice: ").strip()
        
        if choices:
            detection_flags = []
            for choice in choices.split(','):
                choice = choice.strip()
                if choice in self.detection_options:
                    flag = self.detection_options[choice]['flag']
                    if choice == '9':  # Custom script
                        script_name = input("Enter script name: ").strip()
                        flag = f"--script={script_name}"
                    detection_flags.append(flag)
                    print(f"✓ Added: {self.detection_options[choice]['name']}")
            
            self.command_parts['detection'] = ' '.join(detection_flags)

    def get_output_options(self):
        """Get output format and destination"""
        print("\n" + "="*60)
        print("STEP 6: OUTPUT OPTIONS (Optional)")
        print("="*60)
        
        for key, value in self.output_formats.items():
            print(f"{key}. {value['name']:20} ({value['flag']})")
        
        choice = input("\nSelect output format (1-5, or Enter for screen only): ").strip()
        
        if choice in self.output_formats:
            selected = self.output_formats[choice]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get custom filename or use default
            default_name = f"nmap_scan_{timestamp}"
            filename = input(f"Enter filename (or Enter for '{default_name}'): ").strip()
            if not filename:
                filename = default_name
            
            if selected['ext']:
                output_flag = f"{selected['flag']} {filename}{selected['ext']}"
            else:
                output_flag = f"{selected['flag']} {filename}"
            
            self.command_parts['output'] = output_flag
            print(f"✓ Output: {selected['name']} -> {filename}{selected['ext'] if selected['ext'] else '.*'}")

    def get_misc_options(self):
        """Get miscellaneous options"""
        print("\n" + "="*60)
        print("STEP 7: ADDITIONAL OPTIONS (Optional)")
        print("="*60)
        print("Common options:")
        print("  -v    : Verbose output")
        print("  -vv   : Very verbose output")
        print("  -d    : Debug output")
        print("  -n    : No DNS resolution")
        print("  -R    : Always do DNS resolution")
        print("  -Pn   : Skip host discovery")
        print("  -6    : IPv6 scanning")
        print("  --reason : Show reason for port state")
        
        misc = input("\nEnter additional options (space-separated, or Enter for none): ").strip()
        if misc:
            self.command_parts['misc_options'] = misc.split()
            print(f"✓ Additional options: {misc}")

    def build_command(self):
        """Build the final NMAP command"""
        cmd_parts = ['nmap']
        
        # Add scan type
        if self.command_parts['scan_type']:
            cmd_parts.append(self.command_parts['scan_type'])
        
        # Add ports
        if self.command_parts['ports']:
            cmd_parts.append(self.command_parts['ports'])
        
        # Add timing
        if self.command_parts['timing']:
            cmd_parts.append(self.command_parts['timing'])
        
        # Add detection options
        if self.command_parts['detection']:
            cmd_parts.extend(self.command_parts['detection'].split())
        
        # Add output options
        if self.command_parts['output']:
            cmd_parts.extend(self.command_parts['output'].split())
        
        # Add miscellaneous options
        if self.command_parts['misc_options']:
            cmd_parts.extend(self.command_parts['misc_options'])
        
        # Add target (always last)
        cmd_parts.append(self.command_parts['target'])
        
        return ' '.join(cmd_parts)

    def explain_command(self, command):
        """Provide detailed explanation of the command"""
        print("\n" + "="*60)
        print("COMMAND EXPLANATION")
        print("="*60)
        print(f"Command: {command}")
        print("\nBreakdown:")
        
        parts = command.split()
        for i, part in enumerate(parts):
            if part == 'nmap':
                print(f"  {part:15} - Network exploration tool")
            elif part.startswith('-s'):
                scan_type = next((v['name'] for v in self.scan_types.values() if v['flag'] == part), 'Unknown scan')
                print(f"  {part:15} - {scan_type}")
            elif part.startswith('-p'):
                print(f"  {part:15} - Port specification")
            elif part.startswith('-T'):
                timing = next((v['name'] for v in self.timing_templates.values() if v['flag'] == part), 'Unknown timing')
                print(f"  {part:15} - Timing template: {timing}")
            elif part.startswith('-o'):
                output = next((v['name'] for v in self.output_formats.values() if v['flag'] == part), 'Output format')
                print(f"  {part:15} - {output}")
            elif part in ['-v', '-vv', '-d', '-n', '-R', '-Pn', '-6', '--reason']:
                descriptions = {
                    '-v': 'Verbose output',
                    '-vv': 'Very verbose output',
                    '-d': 'Debug output',
                    '-n': 'No DNS resolution',
                    '-R': 'Always do DNS resolution',
                    '-Pn': 'Skip host discovery',
                    '-6': 'IPv6 scanning',
                    '--reason': 'Show reason for port state'
                }
                print(f"  {part:15} - {descriptions.get(part, 'Additional option')}")
            elif i == len(parts) - 1:  # Last part is target
                print(f"  {part:15} - Target specification")

    def save_as_script(self, command):
        """Save command as executable bash script"""
        print("\n" + "="*60)
        print("SAVE AS SCRIPT")
        print("="*60)
        
        save_choice = input("Save this command as a bash script? (y/n): ").strip().lower()
        if save_choice not in ['y', 'yes']:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_script = f"nmap_scan_{timestamp}.sh"
        script_name = input(f"Enter script filename (or Enter for '{default_script}'): ").strip()
        if not script_name:
            script_name = default_script
        
        if not script_name.endswith('.sh'):
            script_name += '.sh'
        
        script_content = f"""#!/bin/bash
# NMAP Scan Script
# Generated by Interactive NMAP Command Builder
# Author: Ross Durrer
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 
# Command explanation:
"""
        
        # Add command breakdown as comments
        parts = command.split()
        for i, part in enumerate(parts):
            if part == 'nmap':
                script_content += f"# {part:15} - Network exploration tool\n"
            elif part.startswith('-'):
                script_content += f"# {part:15} - NMAP option\n"
            elif i == len(parts) - 1:
                script_content += f"# {part:15} - Target specification\n"
        
        script_content += f"\n# Full command:\n{command}\n"
        
        try:
            with open(script_name, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_name, 0o755)
            
            print(f"✓ Script saved as: {script_name}")
            print(f"✓ Made executable with chmod +x")
            print(f"✓ Run with: ./{script_name}")
        except Exception as e:
            print(f"✗ Error saving script: {e}")

    def execute_command(self, command):
        """Execute the NMAP command"""
        print("\n" + "="*60)
        print("EXECUTE SCAN")
        print("="*60)
        
        execute_choice = input("Execute this NMAP command now? (y/n): ").strip().lower()
        if execute_choice not in ['y', 'yes']:
            return
        
        print(f"\nExecuting: {command}")
        print("="*60)
        
        try:
            # Execute the command
            result = subprocess.run(command.split(), text=True, capture_output=False)
            print(f"\n✓ Scan completed with exit code: {result.returncode}")
        except KeyboardInterrupt:
            print("\n✗ Scan interrupted by user")
        except Exception as e:
            print(f"\n✗ Error executing command: {e}")

    def save_command_history(self, command):
        """Save command to history file"""
        history_dir = Path.home() / '.nmap_builder'
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / 'command_history.json'
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        # Add new command
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'target': self.command_parts['target']
        }
        history.append(history_entry)
        
        # Keep only last 50 commands
        history = history[-50:]
        
        # Save history
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save command history: {e}")

    def show_command_history(self):
        """Display command history"""
        history_file = Path.home() / '.nmap_builder' / 'command_history.json'
        
        if not history_file.exists():
            print("No command history found.")
            return
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            print("Error reading command history.")
            return
        
        if not history:
            print("No commands in history.")
            return
        
        print("\n" + "="*60)
        print("COMMAND HISTORY")
        print("="*60)
        
        for i, entry in enumerate(history[-10:], 1):  # Show last 10
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
            print(f"{i:2}. [{timestamp}] {entry['command']}")
        
        choice = input("\nSelect a command to reuse (1-10) or Enter to continue: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= min(10, len(history)):
            selected_command = history[-(11-int(choice))]['command']
            print(f"\nSelected command: {selected_command}")
            return selected_command
        
        return None

    def main_menu(self):
        """Main application menu"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            print("\nMain Menu:")
            print("1. Build New NMAP Command")
            print("2. View Command History")
            print("3. Quick Scan Templates")
            print("4. Help & Documentation")
            print("5. Exit")
            
            choice = input("\nSelect option [1-5]: ").strip()
            
            if choice == '1':
                self.build_new_command()
            elif choice == '2':
                selected_cmd = self.show_command_history()
                if selected_cmd:
                    self.process_built_command(selected_cmd)
            elif choice == '3':
                self.quick_templates()
            elif choice == '4':
                self.show_help()
            elif choice == '5':
                print("\nThank you for using Interactive NMAP Command Builder!")
                print("Author: Ross Durrer | Created: 2025")
                sys.exit(0)
            else:
                input("Invalid choice. Press Enter to continue...")

    def build_new_command(self):
        """Build a new NMAP command interactively"""
        self.clear_screen()
        self.print_banner()
        
        # Reset command parts
        self.command_parts = {
            'scan_type': '',
            'target': '',
            'ports': '',
            'timing': '',
            'detection': '',
            'output': '',
            'misc_options': []
        }
        
        # Interactive steps
        self.get_scan_type()
        self.get_target()
        self.get_port_specification()
        self.get_timing_template()
        self.get_detection_options()
        self.get_output_options()
        self.get_misc_options()
        
        # Build and process command
        command = self.build_command()
        self.process_built_command(command)

    def process_built_command(self, command):
        """Process the built command with various options"""
        self.clear_screen()
        print("="*60)
        print("GENERATED NMAP COMMAND")
        print("="*60)
        print(f"\n{command}\n")
        
        # Show explanation
        self.explain_command(command)
        
        # Save to history
        self.save_command_history(command)
        
        # Options menu
        while True:
            print("\n" + "="*60)
            print("OPTIONS")
            print("="*60)
            print("1. Execute scan now")
            print("2. Save as bash script")
            print("3. Copy to clipboard")
            print("4. Modify command")
            print("5. Return to main menu")
            
            choice = input("\nSelect option [1-5]: ").strip()
            
            if choice == '1':
                self.execute_command(command)
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.save_as_script(command)
                input("\nPress Enter to continue...")
            elif choice == '3':
                try:
                    import pyperclip
                    pyperclip.copy(command)
                    print("✓ Command copied to clipboard!")
                except ImportError:
                    print("✗ pyperclip not installed. Install with: pip install pyperclip")
                input("\nPress Enter to continue...")
            elif choice == '4':
                new_command = input(f"Edit command:\n{command}\n\nEnter modified command: ").strip()
                if new_command:
                    command = new_command
                    print("✓ Command updated!")
                continue
            elif choice == '5':
                break
            else:
                input("Invalid choice. Press Enter to continue...")

    def quick_templates(self):
        """Predefined scan templates"""
        self.clear_screen()
        print("="*60)
        print("QUICK SCAN TEMPLATES")
        print("="*60)
        
        templates = {
            '1': {
                'name': 'Quick Host Discovery',
                'command': 'nmap -sn {target}',
                'description': 'Fast ping scan to discover live hosts'
            },
            '2': {
                'name': 'Fast TCP Scan',
                'command': 'nmap -F {target}',
                'description': 'Scan top 100 most common ports'
            },
            '3': {
                'name': 'Comprehensive Scan',
                'command': 'nmap -sS -sV -O -A {target}',
                'description': 'SYN scan with version and OS detection'
            },
            '4': {
                'name': 'Stealth Scan',
                'command': 'nmap -sS -T1 -f {target}',
                'description': 'Slow, fragmented SYN scan for IDS evasion'
            },
            '5': {
                'name': 'UDP Service Scan',
                'command': 'nmap -sU --top-ports 20 {target}',
                'description': 'Scan top 20 UDP ports'
            },
            '6': {
                'name': 'Vulnerability Scan',
                'command': 'nmap -sV --script=vuln {target}',
                'description': 'Version detection with vulnerability scripts'
            },
            '7': {
                'name': 'Web Server Scan',
                'command': 'nmap -p 80,443 -sV --script=http-* {target}',
                'description': 'Focus on web services with HTTP scripts'
            },
            '8': {
                'name': 'Full Port Scan',
                'command': 'nmap -p- -T4 {target}',
                'description': 'Scan all 65535 ports (aggressive timing)'
            }
        }
        
        for key, template in templates.items():
            print(f"{key}. {template['name']:20} - {template['description']}")
        
        choice = input("\nSelect template [1-8] or Enter to return: ").strip()
        
        if choice in templates:
            template = templates[choice]
            target = input(f"\nEnter target for '{template['name']}': ").strip()
            if target:
                command = template['command'].format(target=target)
                self.process_built_command(command)
        
        if choice:
            input("\nPress Enter to continue...")

    def show_help(self):
        """Show help and documentation"""
        self.clear_screen()
        print("="*60)
        print("HELP & DOCUMENTATION")
        print("="*60)
        
        help_text = """
NMAP COMMAND BUILDER HELP

This tool helps you build NMAP commands interactively by guiding you through
the most common options and explaining what each parameter does.

KEY FEATURES:
• Interactive command building with explanations
• Save commands as executable bash scripts
• Command history tracking
• Quick scan templates
• Educational mode showing command breakdown

COMMON NMAP OPTIONS:
• -sS: TCP SYN scan (default, requires root)
• -sT: TCP connect scan (works without root)
• -sU: UDP scan (slower but important)
• -sV: Version detection
• -O:  OS detection
• -A:  Aggressive scan (OS, version, scripts)
• -p:  Port specification
• -T:  Timing templates (0=paranoid, 5=insane)
• -v:  Verbose output
• -oN: Normal output to file

TARGET FORMATS:
• Single IP: 192.168.1.1
• Range: 192.168.1.1-254
• CIDR: 192.168.1.0/24
• Hostname: example.com
• File: -iL targets.txt

AUTHOR: Ross Durrer
CREATED: 2025

For more information about NMAP, visit: https://nmap.org/
"""
        print(help_text)
        input("\nPress Enter to return to main menu...")

    def run(self):
        """Main application entry point"""
        if not self.check_nmap_installed():
            sys.exit(1)
        
        self.main_menu()

def main():
    """Application entry point"""
    parser = argparse.ArgumentParser(
        description="Interactive NMAP Command Builder by Ross Durrer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nmap_builder.py              # Interactive mode
  python nmap_builder.py --help       # Show this help
        """
    )
    
    parser.add_argument('--version', action='version', version='NMAP Command Builder 1.0 by Ross Durrer (2025)')
    
    args = parser.parse_args()
    
    try:
        app = NmapBuilder()
        app.run()
    except KeyboardInterrupt:
        print("\n\nExiting... Thank you for using NMAP Command Builder!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()