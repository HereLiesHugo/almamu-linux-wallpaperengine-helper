# Linux Wallpaper Engine Helper

A user-friendly interactive configuration tool for [Almamu's Linux Wallpaper Engine](https://github.com/Almamu/linux-wallpaperengine) that simplifies the setup and management of animated wallpapers on Linux systems.

## Features

- **Interactive Menu System**: Navigate through configuration options with arrow keys
- **Multi-Screen Support**: Configure different wallpapers for each display
- **Window Mode**: Run wallpapers as floating windows with custom positioning
- **Performance Optimization**: Configure FPS, fullscreen pause behavior
- **Audio Control**: Volume management, auto-mute, and audio processing options
- **Interaction Settings**: Mouse and parallax effect controls
- **Screenshot Capabilities**: Capture wallpaper screenshots with customizable delays
- **Command Export**: Save generated commands to `wallpaper-command.txt` for reuse

## Requirements

- Linux system with X11 display server
- `linux-wallpaperengine` executable in the same directory
- Python 3.6 or higher
- `xrandr` utility for display detection

## Installation

1. Clone or download this repository
2. Ensure `linux-wallpaperengine` is in the same directory as the script
3. Make the script executable:
   ```bash
   chmod +x set-wallpaper-display.py
   ```

## Usage

Run the configuration tool:
```bash
./set-wallpaper-display.py
```

### Navigation

- **↑/↓ Arrow Keys**: Navigate menu options
- **Enter**: Select current option
- **q**: Quit current menu/exit

### Configuration Workflow

1. **Background Mode Selection**
   - Single background (all screens)
   - Multiple backgrounds (per screen)
   - Window mode (floating window)

2. **Background Configuration**
   - Enter wallpaper ID or local path
   - For multi-screen: configure each display individually
   - Set scaling modes (stretch, fit, fill)
   - Configure clamping options

3. **Performance Settings**
   - Frame rate limit (1-240 FPS)
   - Fullscreen pause behavior

4. **Sound Settings**
   - Volume control or silent mode
   - Auto-mute toggle
   - Audio processing options

5. **Interaction Settings**
   - Mouse interaction enable/disable
   - Parallax effect controls

6. **Screenshot Options** (Optional)
   - Enable screenshot capture
   - Set output format (PNG, JPEG, BMP)
   - Configure frame delay

7. **Review and Execute**
   - Preview the generated command
   - Execute directly
   - Save command to file
   - Both execute and save

## Command Export

The tool can save your configured command to `wallpaper-command.txt` for:
- Scripting and automation
- Sharing configurations
- Quick re-execution without reconfiguration

## Display Detection

The tool automatically detects connected displays using `xrandr` and attempts to identify monitor names through EDID data. Supported displays include:
- HDMI connections (HDMI-1, HDMI-2, etc.)
- DisplayPort connections (DP-1, DP-2, etc.)
- Embedded displays (eDP-1, eDP-2, etc.)

## Examples

### Single Background
```
./linux-wallpaperengine --fps 30 2317494988
```

### Multi-Screen Setup
```
./linux-wallpaperengine --screen-root HDMI-1 --bg wallpaper1 --scaling fit \
                        --screen-root DP-1 --bg wallpaper2 --scaling stretch \
                        --fps 60 --volume 50
```

### Window Mode
```
./linux-wallpaperengine --window 100x100x800x600 2317494988
```

## Troubleshooting

### Common Issues

1. **"linux-wallpaperengine not found"**
   - Ensure the executable is in the same directory as the script
   - Check file permissions

2. **Display detection issues**
   - Verify `xrandr` is installed and working
   - Check display connections

3. **Command execution failures**
   - Review the generated command in the preview
   - Save the command and test manually

### Getting Help

- Use the arrow keys to navigate menus
- Press 'q' at any time to return to the previous menu
- The command preview shows exactly what will be executed

## Contributing

Feel free to submit issues and enhancement requests!

## License

[GNU General Public License v3.0](LICENSE)
