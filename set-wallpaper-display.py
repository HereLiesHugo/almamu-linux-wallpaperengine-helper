#!/usr/bin/env python3
import os
import sys
import subprocess
from subprocess import CalledProcessError
import shutil
import json
from typing import List, Dict, Optional, Tuple

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Foreground
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header(title):
    clear_screen()
    print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}╔════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}║{Colors.RESET} {title:^42} {Colors.BRIGHT_BLUE}{Colors.BOLD}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD}╚════════════════════════════════════════════╝{Colors.RESET}")
    print()

def print_menu(title: str, options: List[str], selected_idx: int, show_instructions: bool = True):
    print_header(title)
    for i, option in enumerate(options):
        if i == selected_idx:
            print(f"{Colors.BG_BLUE}{Colors.BOLD}► {option}{Colors.RESET}")
        else:
            print(f"  {option}")
    print()
    if show_instructions:
        print(f"{Colors.DIM}Use ↑/↓ arrows to navigate, {Colors.BOLD}Enter{Colors.DIM} to select, {Colors.BOLD}q{Colors.DIM} to quit{Colors.RESET}")

def get_key():
    """Get arrow key input"""
    import sys
    import tty
    import termios
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        
        if ch == '\x1b':  # Escape sequence
            next1 = sys.stdin.read(1)
            next2 = sys.stdin.read(1)
            if next1 == '[':
                if next2 == 'A':
                    return 'up'
                elif next2 == 'B':
                    return 'down'
                elif next2 == 'C':
                    return 'right'
                elif next2 == 'D':
                    return 'left'
        elif ch == '\r' or ch == '\n':
            return 'enter'
        elif ch in ['q', 'Q']:
            return 'q'
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_text_input(prompt: str, default: str = "", allow_empty: bool = False) -> Optional[str]:
    """Get text input from user"""
    print_header("Input Required")
    print(f"{Colors.YELLOW}{prompt}{Colors.RESET}")
    if default:
        print(f"{Colors.DIM}(default: {Colors.CYAN}{default}{Colors.DIM}){Colors.RESET}")
    print()
    
    try:
        value = input(f"{Colors.GREEN}→{Colors.RESET} ").strip()
        if not value and default:
            return default
        if not value and not allow_empty:
            return None
        return value
    except KeyboardInterrupt:
        return None

def get_numeric_input(prompt: str, min_val: int = 0, max_val: int = 100, default: int = 50) -> Optional[int]:
    """Get numeric input from user"""
    while True:
        value = get_text_input(f"{prompt} ({min_val}-{max_val})", str(default))
        if value is None:
            return None
        try:
            num = int(value)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"{Colors.RED}Value must be between {min_val} and {max_val}{Colors.RESET}")
                input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid number{Colors.RESET}")
            input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def get_available_displays() -> List[Tuple[str, str]]:
    """Get available displays using xrandr - returns (port, label) tuples with name and resolution"""
    try:
        result = subprocess.check_output(['xrandr', '--query'], text=True)
        displays = []
        for line in result.split('\n'):
            if ' connected' in line:
                parts = line.split()
                port_name = parts[0]
                
                # Extract resolution if available (format: 1920x1080+0+0)
                resolution = ""
                for part in parts[1:]:
                    if 'x' in part and ('+' in part or part[0].isdigit()):
                        resolution = part.split('+')[0]  # Get just the resolution part
                        break
                
                # Try to get monitor name using EDID
                monitor_name = get_monitor_name(port_name)
                
                if resolution and monitor_name:
                    display_label = f"{port_name} - {monitor_name} ({resolution})"
                elif resolution:
                    display_label = f"{port_name} ({resolution})"
                elif monitor_name:
                    display_label = f"{port_name} - {monitor_name}"
                else:
                    display_label = port_name
                
                displays.append((port_name, display_label))
        
        return displays if displays else [('HDMI-1', 'HDMI-1'), ('DP-1', 'DP-1')]
    except Exception:
        return [('HDMI-1', 'HDMI-1'), ('DP-1', 'DP-1'), ('eDP-1', 'eDP-1')]

def get_monitor_name(port_name: str) -> str:
    """Get monitor name using xrandr --prop or EDID data"""
    try:
        # Try to get monitor name from xrandr properties
        result = subprocess.check_output(['xrandr', '--prop'], text=True)
        lines = result.split('\n')
        
        current_monitor = None
        for i, line in enumerate(lines):
            if port_name in line and ' connected' in line:
                current_monitor = port_name
                # Look for monitor name in the next few lines
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()
                    if 'Monitor name:' in next_line:
                        return next_line.split(':', 1)[1].strip()
                    elif 'EDID:' in next_line:
                        # Parse EDID to get monitor name
                        edid_data = []
                        for k in range(j + 1, min(j + 8, len(lines))):
                            edid_line = lines[k].strip()
                            if edid_line.startswith('\t') and len(edid_line) > 1:
                                edid_data.append(edid_line.strip())
                            else:
                                break
                        
                        if edid_data:
                            return parse_edid_for_name(edid_data)
                    elif next_line and not next_line.startswith('\t') and current_monitor:
                        # Reached next monitor section
                        break
                break
        
        return ""
    except Exception:
        return ""

def parse_edid_for_name(edid_lines: List[str]) -> str:
    """Parse EDID data to extract monitor name"""
    try:
        # Combine EDID hex data
        edid_hex = ''.join(line.replace('\t', '') for line in edid_lines)
        
        # Look for monitor name in EDID (typically in descriptor blocks)
        # EDID descriptor blocks start at offset 0x36 and every 18 bytes after
        if len(edid_hex) >= 256:  # Minimum EDID length
            # Check descriptor blocks for monitor name
            for offset in [0x36, 0x48, 0x5A, 0x6C]:
                if offset + 18 <= len(edid_hex) // 2:
                    descriptor = edid_hex[offset*2:(offset+18)*2]
                    # Check if this is a text descriptor (first byte 0x00)
                    if descriptor.startswith('00'):
                        # Extract ASCII text from descriptor
                        text_bytes = bytes.fromhex(descriptor[6:26])
                        text = text_bytes.decode('ascii', errors='ignore').strip('\x00\x0a\x0d')
                        if text and len(text) > 0 and text.isprintable():
                            return text
        
        return ""
    except Exception:
        return ""

def log(content: str, level: str = "info"):
    levels = {
        "info": f"{Colors.CYAN}ℹ{Colors.RESET}",
        "success": f"{Colors.GREEN}✓{Colors.RESET}",
        "error": f"{Colors.RED}✗{Colors.RESET}",
        "warning": f"{Colors.YELLOW}⚠{Colors.RESET}",
    }
    symbol = levels.get(level, levels["info"])
    print(f"{symbol} {content}")

class WallpaperConfig:
    def __init__(self):
        self.background_id = ""
        self.screens: List[Dict] = []  # List of {screen, bg, scaling, clamp}
        self.window_geometries: List[str] = []
        self.fps = 30
        self.volume = 15
        self.silent = False
        self.noautomute = False
        self.no_audio_processing = False
        self.no_fullscreen_pause = False
        self.disable_mouse = False
        self.disable_parallax = False
        self.screenshot_path = ""
        self.screenshot_delay = 5
        self.assets_dir = ""
        self.properties: List[str] = []

def select_background_mode() -> Optional[str]:
    """Select between single background or multi-screen"""
    options = [
        "Single background (all screens)",
        "Multiple backgrounds (per screen)",
        "Window mode (floating window)",
        "Cancel"
    ]
    
    selected = 0
    while True:
        print_menu("Background Mode", options, selected)
        
        key = get_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:
                return 'single'
            elif selected == 1:
                return 'multi'
            elif selected == 2:
                return 'window'
            else:
                return None
        elif key == 'q':
            return None

def configure_single_background(config: WallpaperConfig) -> bool:
    """Configure a single background for all screens"""
    print_header("Background Configuration")
    print(f"{Colors.YELLOW}Enter background ID or path:{Colors.RESET}")
    print(f"{Colors.DIM}Examples: {Colors.CYAN}2317494988{Colors.RESET} or {Colors.CYAN}./my-wallpaper{Colors.RESET}")
    print()
    
    bg = input(f"{Colors.GREEN}→{Colors.RESET} ").strip()
    if not bg:
        return False
    
    config.background_id = bg
    return True

def configure_window_mode(config: WallpaperConfig) -> bool:
    """Configure window mode"""
    print_header("Window Mode Configuration")
    print(f"{Colors.YELLOW}Enter background ID or path:{Colors.RESET}")
    print()
    
    bg = input(f"{Colors.GREEN}→{Colors.RESET} ").strip()
    if not bg:
        return False
    
    config.background_id = bg
    
    # Get window geometry
    print()
    print(f"{Colors.YELLOW}Enter window geometry (X x Y x W x H):{Colors.RESET}")
    print(f"{Colors.DIM}Example: 0x0x1920x1080{Colors.RESET}")
    print()
    
    geometry = input(f"{Colors.GREEN}→{Colors.RESET} ").strip()
    if geometry:
        config.window_geometries.append(geometry)
    
    return True

def configure_multi_screen(config: WallpaperConfig) -> bool:
    """Configure multiple backgrounds for different screens"""
    displays = get_available_displays()
    display_labels = [label for _, label in displays]
    display_ports = [port for port, _ in displays]
    
    while True:
        print_header("Multi-Screen Configuration")
        print(f"{Colors.BRIGHT_CYAN}Configured screens: {len(config.screens)}{Colors.RESET}")
        print()
        
        for i, screen in enumerate(config.screens):
            print(f"{Colors.CYAN}{i+1}. {screen['screen']} → {screen['bg']}{Colors.RESET}")
            if screen['scaling']:
                print(f"   {Colors.DIM}Scaling: {screen['scaling']}{Colors.RESET}")
            if screen['clamp']:
                print(f"   {Colors.DIM}Clamping: {screen['clamp']}{Colors.RESET}")
        
        print()
        
        options = [
            "Add screen",
            "Remove screen",
            "Configure default background",
            "Done"
        ]
        
        selected = 0
        while True:
            print(f"{Colors.DIM}Navigate with arrows, press Enter to select{Colors.RESET}")
            print()
            for i, option in enumerate(options):
                if i == selected:
                    print(f"{Colors.BG_BLUE}{Colors.BOLD}► {option}{Colors.RESET}")
                else:
                    print(f"  {option}")
            
            key = get_key()
            if key == 'up':
                selected = (selected - 1) % len(options)
            elif key == 'down':
                selected = (selected + 1) % len(options)
            elif key == 'enter':
                break
            elif key == 'q':
                return False
        
        if selected == 0:  # Add screen
            # Select display
            screen_selected = 0
            display_confirmed = False
            while True:
                print_menu("Select Display", display_labels, screen_selected)
                key = get_key()
                if key == 'up':
                    screen_selected = (screen_selected - 1) % len(display_labels)
                elif key == 'down':
                    screen_selected = (screen_selected + 1) % len(display_labels)
                elif key == 'enter':
                    display_confirmed = True
                    break
                elif key == 'q':
                    break
            
            if not display_confirmed:
                continue
            
            display = display_ports[screen_selected]
            
            # Get background
            bg = get_text_input(f"Background for {display} (ID or path):", allow_empty=False)
            if not bg:
                continue
            
            # Get scaling
            scaling_options = ["None", "stretch", "fit", "fill"]
            scaling_idx = 0
            while True:
                print_menu("Scaling Mode", scaling_options, scaling_idx)
                key = get_key()
                if key == 'up':
                    scaling_idx = (scaling_idx - 1) % len(scaling_options)
                elif key == 'down':
                    scaling_idx = (scaling_idx + 1) % len(scaling_options)
                elif key == 'enter':
                    break
                elif key == 'q':
                    break
            
            scaling = None if scaling_options[scaling_idx] == "None" else scaling_options[scaling_idx]
            
            # Get clamping
            clamp_options = ["None", "clamp", "border", "repeat"]
            clamp_idx = 0
            while True:
                print_menu("Clamping Mode", clamp_options, clamp_idx)
                key = get_key()
                if key == 'up':
                    clamp_idx = (clamp_idx - 1) % len(clamp_options)
                elif key == 'down':
                    clamp_idx = (clamp_idx + 1) % len(clamp_options)
                elif key == 'enter':
                    break
                elif key == 'q':
                    break
            
            clamp = None if clamp_options[clamp_idx] == "None" else clamp_options[clamp_idx]
            
            config.screens.append({
                'screen': display,
                'bg': bg,
                'scaling': scaling,
                'clamp': clamp
            })
        
        elif selected == 1:  # Remove screen
            if config.screens:
                screens_list = [f"{s['screen']} → {s['bg']}" for s in config.screens]
                remove_idx = 0
                while True:
                    print_menu("Select Screen to Remove", screens_list, remove_idx)
                    key = get_key()
                    if key == 'up':
                        remove_idx = (remove_idx - 1) % len(screens_list)
                    elif key == 'down':
                        remove_idx = (remove_idx + 1) % len(screens_list)
                    elif key == 'enter':
                        config.screens.pop(remove_idx)
                        break
                    elif key == 'q':
                        break
        
        elif selected == 2:  # Configure default
            bg = get_text_input("Default background (ID or path):", allow_empty=True)
            if bg:
                config.background_id = bg
        
        else:  # Done
            if not config.screens and not config.background_id:
                log("Please configure at least one screen or a default background", "error")
                input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
                continue
            return True

def configure_performance(config: WallpaperConfig) -> bool:
    """Configure performance settings"""
    options = [
        f"FPS: {config.fps}",
        f"Fullscreen pause: {'Disabled' if config.no_fullscreen_pause else 'Enabled'}",
        "Done"
    ]
    
    selected = 0
    while True:
        print_menu("Performance Settings", options, selected)
        
        key = get_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:
                fps = get_numeric_input("Frame rate limit", 1, 240, config.fps)
                if fps is not None:
                    config.fps = fps
                    options[0] = f"FPS: {config.fps}"
            elif selected == 1:
                config.no_fullscreen_pause = not config.no_fullscreen_pause
                options[1] = f"Fullscreen pause: {'Disabled' if config.no_fullscreen_pause else 'Enabled'}"
            else:
                return True
        elif key == 'q':
            return False
    
    return True

def configure_sound(config: WallpaperConfig) -> bool:
    """Configure sound settings"""
    selected = 0
    
    while True:
        options = [
            f"Volume: {config.volume}" if not config.silent else "Mode: Silent",
            f"Auto-mute: {'Disabled' if config.noautomute else 'Enabled'}",
            f"Audio processing: {'Disabled' if config.no_audio_processing else 'Enabled'}",
            "Done"
        ]
        
        print_menu("Sound Settings", options, selected)
        
        key = get_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:
                # Toggle silent/normal mode
                if config.silent:
                    config.silent = False
                    config.volume = get_numeric_input("Volume", 0, 100, 15) or 15
                else:
                    mode_opts = ["Silent", "With volume control"]
                    mode_idx = 0
                    while True:
                        print_menu("Sound Mode", mode_opts, mode_idx)
                        key = get_key()
                        if key == 'up':
                            mode_idx = (mode_idx - 1) % len(mode_opts)
                        elif key == 'down':
                            mode_idx = (mode_idx + 1) % len(mode_opts)
                        elif key == 'enter':
                            break
                        elif key == 'q':
                            break
                    
                    if mode_idx == 0:
                        config.silent = True
                    else:
                        config.volume = get_numeric_input("Volume", 0, 100, 15) or 15
            elif selected == 1:
                config.noautomute = not config.noautomute
            elif selected == 2:
                config.no_audio_processing = not config.no_audio_processing
            else:
                return True
        elif key == 'q':
            return False
    
    return True

def configure_interaction(config: WallpaperConfig) -> bool:
    """Configure interaction settings"""
    selected = 0
    
    while True:
        options = [
            f"Mouse: {'Disabled' if config.disable_mouse else 'Enabled'}",
            f"Parallax: {'Disabled' if config.disable_parallax else 'Enabled'}",
            "Done"
        ]
        
        print_menu("Interaction Settings", options, selected)
        
        key = get_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:
                config.disable_mouse = not config.disable_mouse
            elif selected == 1:
                config.disable_parallax = not config.disable_parallax
            else:
                return True
        elif key == 'q':
            return False
    
    return True

def configure_screenshot(config: WallpaperConfig) -> bool:
    """Configure screenshot options"""
    selected = 0
    
    while True:
        options = [
            "Enable/Disable",
            f"Delay: {config.screenshot_delay} frames",
            "Done"
        ]
        
        print_menu("Screenshot Options", options, selected)
        
        if config.screenshot_path:
            print(f"{Colors.CYAN}Screenshot path: {config.screenshot_path}{Colors.RESET}\n")
        
        key = get_key()
        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:
                if config.screenshot_path:
                    config.screenshot_path = ""
                else:
                    path = get_text_input("Screenshot file path (PNG, JPEG, BMP):", "", allow_empty=False)
                    if path:
                        config.screenshot_path = path
            elif selected == 1:
                delay = get_numeric_input("Frame delay", 0, 1000, config.screenshot_delay)
                if delay is not None:
                    config.screenshot_delay = delay
            else:
                return True
        elif key == 'q':
            return False
    
    return True

def build_command(config: WallpaperConfig, exe_path: str) -> List[str]:
    """Build the command line"""
    cmd = [exe_path]
    
    if config.fps != 30:
        cmd.extend(['--fps', str(config.fps)])
    
    if config.no_fullscreen_pause:
        cmd.append('--no-fullscreen-pause')
    
    if config.silent:
        cmd.append('--silent')
    elif config.volume != 15:
        cmd.extend(['--volume', str(config.volume)])
    
    if config.noautomute:
        cmd.append('--noautomute')
    
    if config.no_audio_processing:
        cmd.append('--no-audio-processing')
    
    if config.disable_mouse:
        cmd.append('--disable-mouse')
    
    if config.disable_parallax:
        cmd.append('--disable-parallax')
    
    if config.screenshot_path:
        cmd.extend(['--screenshot', config.screenshot_path])
        if config.screenshot_delay != 5:
            cmd.extend(['--screenshot-delay', str(config.screenshot_delay)])
    
    if config.assets_dir:
        cmd.extend(['--assets-dir', config.assets_dir])
    
    # Add screen configurations
    for screen in config.screens:
        cmd.extend(['--screen-root', screen['screen']])
        cmd.extend(['--bg', screen['bg']])
        if screen['scaling']:
            cmd.extend(['--scaling', screen['scaling']])
        if screen['clamp']:
            cmd.extend(['--clamp', screen['clamp']])
    
    # Add window geometries
    for geometry in config.window_geometries:
        cmd.extend(['--window', geometry])
    
    # Add properties
    for prop in config.properties:
        cmd.extend(['--set-property', prop])
    
    # Add background ID
    if config.background_id:
        cmd.append(config.background_id)
    
    return cmd

def confirm_and_execute(config: WallpaperConfig, exe_path: str) -> bool:
    """Show command and confirm execution"""
    cmd = build_command(config, exe_path)
    
    print_header("Review Configuration")
    
    print(f"{Colors.BRIGHT_CYAN}Command to execute:{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}{' '.join(cmd)}{Colors.RESET}")
    print()
    
    # Summary
    print(f"{Colors.BRIGHT_CYAN}Configuration Summary:{Colors.RESET}")
    if config.background_id:
        print(f"  • Background: {Colors.CYAN}{config.background_id}{Colors.RESET}")
    if config.screens:
        print(f"  • Screens configured: {Colors.CYAN}{len(config.screens)}{Colors.RESET}")
    print(f"  • FPS: {Colors.CYAN}{config.fps}{Colors.RESET}")
    if config.silent:
        print(f"  • Sound: {Colors.CYAN}Silent{Colors.RESET}")
    else:
        print(f"  • Volume: {Colors.CYAN}{config.volume}{Colors.RESET}")
    
    print()
    
    options = ["Execute", "Save command", "Execute & Save", "Cancel"]
    selected = 0
    
    while True:
        print(f"{Colors.DIM}Navigate with arrows, press Enter to select{Colors.RESET}")
        print()
        for i, option in enumerate(options):
            if i == selected:
                print(f"{Colors.BG_BLUE}{Colors.BOLD}► {option}{Colors.RESET}")
            else:
                print(f"  {option}")
        
        key = get_key()
        if key == 'up' or key == 'left':
            selected = (selected - 1) % len(options)
        elif key == 'down' or key == 'right':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            if selected == 0:  # Execute only
                execute_command(cmd)
                return True
            elif selected == 1:  # Save command only
                save_command_to_file(cmd)
                return False
            elif selected == 2:  # Execute & Save
                execute_command(cmd)
                save_command_to_file(cmd)
                return True
            else:  # Cancel
                return False
        elif key == 'q':
            return False

def execute_command(cmd: List[str]):
    """Execute the command"""
    print_header("Executing")
    print(f"{Colors.YELLOW}Running wallpaper engine...{Colors.RESET}")
    print()
    
    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        log(f"Error: {e}", "error")
    
    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def save_command_to_file(cmd: List[str]):
    """Save the command to wallpaper-command.txt"""
    try:
        with open('wallpaper-command.txt', 'w') as f:
            f.write(' '.join(cmd))
        log("Command saved to wallpaper-command.txt", "success")
    except Exception as e:
        log(f"Error saving command: {e}", "error")
    
    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def main():
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linux-wallpaperengine')
    
    if not os.path.exists(exe_path):
        print(f"{Colors.RED}Error: linux-wallpaperengine not found{Colors.RESET}")
        sys.exit(1)
    
    clear_screen()
    
    while True:
        print_header("Linux Wallpaper Engine - Display Configuration")
        
        print(f"{Colors.BRIGHT_GREEN}Welcome to the wallpaper configurator!{Colors.RESET}")
        print()
        print(f"{Colors.DIM}This tool will guide you through configuring your wallpaper setup.{Colors.RESET}")
        print()
        
        options = [
            "Start new configuration",
            "Exit"
        ]
        
        selected = 0
        while True:
            print(f"{Colors.DIM}Navigate with arrows, press Enter to select{Colors.RESET}")
            print()
            for i, option in enumerate(options):
                if i == selected:
                    print(f"{Colors.BG_BLUE}{Colors.BOLD}► {option}{Colors.RESET}")
                else:
                    print(f"  {option}")
            
            key = get_key()
            if key == 'up':
                selected = (selected - 1) % len(options)
            elif key == 'down':
                selected = (selected + 1) % len(options)
            elif key == 'enter':
                break
            elif key == 'q':
                clear_screen()
                log("Goodbye!", "success")
                sys.exit(0)
        
        if selected == 1:
            clear_screen()
            log("Goodbye!", "success")
            sys.exit(0)
        
        # Create config
        config = WallpaperConfig()
        
        # 1. Select background mode
        mode = select_background_mode()
        if mode is None:
            continue
        
        # 2. Configure background
        if mode == 'single':
            if not configure_single_background(config):
                continue
        elif mode == 'multi':
            if not configure_multi_screen(config):
                continue
        elif mode == 'window':
            if not configure_window_mode(config):
                continue
        
        # 3. Performance settings
        if not configure_performance(config):
            continue
        
        # 4. Sound settings
        if not configure_sound(config):
            continue
        
        # 5. Interaction settings
        if not configure_interaction(config):
            continue
        
        # 6. Screenshot (optional)
        screenshot_opts = ["Configure", "Skip"]
        ss_idx = 0
        while True:
            print_menu("Screenshot Options", screenshot_opts, ss_idx)
            key = get_key()
            if key == 'up':
                ss_idx = (ss_idx - 1) % len(screenshot_opts)
            elif key == 'down':
                ss_idx = (ss_idx + 1) % len(screenshot_opts)
            elif key == 'enter':
                if ss_idx == 0:
                    if not configure_screenshot(config):
                        continue
                break
            elif key == 'q':
                break
        
        # 7. Review and confirm
        if confirm_and_execute(config, exe_path):
            pass
        
        input(f"\n{Colors.DIM}Press Enter to continue to main menu...{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        log("Interrupted by user", "warning")
        sys.exit(0)

