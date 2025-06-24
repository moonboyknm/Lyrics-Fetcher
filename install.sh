#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
MUSIC_NOTE="🎵"
CHECK_MARK="✅"
CROSS_MARK="❌"
ROCKET="🚀"
GEAR="⚙️"
FOLDER="📁"

echo -e "${PURPLE}${MUSIC_NOTE} LYRICS-CLI INSTALLER ${MUSIC_NOTE}${NC}"
echo -e "${CYAN}===============================================${NC}"
echo -e "${BLUE}A command-line tool to search and download song lyrics${NC}"
echo -e "${CYAN}===============================================${NC}"
echo

# Function to print colored output
print_status() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${GEAR} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   echo "Please run as a regular user:"
   echo "  bash install.sh"
   exit 1
fi

# Check if Python 3 is installed
print_info "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    echo "Please install Python 3 first:"
    echo "  sudo pacman -S python python-pip"
    exit 1
fi

python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
print_status "Found Python $python_version"

# Check if pip is installed
print_info "Checking pip installation..."
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    print_error "pip is not installed."
    echo "Please install pip first:"
    echo "  sudo pacman -S python-pip"
    exit 1
fi

print_status "pip is available"

# Check if git is installed (for cloning)
# This check is more relevant if the script itself does the cloning.
# If the user is expected to clone manually, this can be less critical.
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed. This might be needed if you cloned the repository."
    # Removed automatic git install as it's better to tell user or assume pre-cloned state.
fi

# Create default lyrics directory
DEFAULT_LYRICS_DIR="$HOME/Documents/Obsidian/Lyrics"
print_info "Creating default lyrics directory..."
if mkdir -p "$DEFAULT_LYRICS_DIR"; then
    print_status "Created directory: $DEFAULT_LYRICS_DIR"
else
    print_error "Failed to create directory: $DEFAULT_LYRICS_DIR"
    exit 1
fi

# Install the package
print_info "Installing lyrics-cli via pip..."

# Ensure setup.py exists before attempting installation
if [[ ! -f "setup.py" ]]; then
    print_error "setup.py not found in the current directory."
    echo "Please run this script from the root directory of the Lyrics-Fetcher project."
    exit 1
fi

# Perform the standard user installation using setup.py
python3 -m pip install --user .
INSTALL_STATUS=$?

if [[ $INSTALL_STATUS -eq 0 ]]; then
    print_status "Successfully installed lyrics-cli!"
else
    print_error "Failed to install lyrics-cli."
    echo "Attempting to clean up and retry installation..."
    # Attempt a clean uninstall before retrying, for robustness
    python3 -m pip uninstall -y lyrics-cli 2>/dev/null # Suppress errors if not installed
    python3 -m pip install --user .
    INSTALL_STATUS=$?

    if [[ $INSTALL_STATUS -ne 0 ]]; then
        print_error "Installation failed even after retry. Please check the output above for errors."
        exit 1
    fi
fi

# Check if ~/.local/bin is in PATH
print_info "Checking PATH configuration..."
LOCAL_BIN="$HOME/.local/bin"
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    print_warning "$LOCAL_BIN is not in your PATH"
    echo
    echo "To use lyrics-cli from anywhere, add this line to your shell config:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
    echo
    echo "Then restart your shell or run:"
    echo "  source ~/.bashrc  # or ~/.zshrc"
    echo
    
    # Ask if user wants to add to PATH automatically
    echo -n "Would you like to add $LOCAL_BIN to your PATH automatically? (y/n): "
    read -r add_to_path
    
    if [[ $add_to_path =~ ^[Yy]$ ]]; then
        # Detect shell and add to appropriate config
        if [[ -n "$ZSH_VERSION" ]]; then
            # User is running zsh
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            print_status "Added to ~/.zshrc"
        elif [[ -n "$BASH_VERSION" ]]; then
            # User is running bash
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            print_status "Added to ~/.bashrc"
        else
            # Try to detect based on available config files
            if [[ -f "$HOME/.zshrc" ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
                print_status "Added to ~/.zshrc"
            elif [[ -f "$HOME/.bashrc" ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                print_status "Added to ~/.bashrc"
            else
                print_warning "Could not detect shell config file. Please add manually."
            fi
        fi
        
        print_info "Please restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    fi
else
    print_status "PATH is already configured correctly"
fi

# Create a config file
print_info "Creating configuration file..."
CONFIG_DIR="$HOME/.config/lyrics-cli"
mkdir -p "$CONFIG_DIR"

# Check if config.json already exists before creating.
# If it exists, offer to overwrite or skip.
if [[ -f "$CONFIG_DIR/config.json" ]]; then
    print_warning "Configuration file already exists at $CONFIG_DIR/config.json."
    echo -n "Overwrite with default configuration? (y/n): "
    read -r overwrite_config
    if [[ ! $overwrite_config =~ ^[Yy]$ ]]; then
        print_status "Skipping config file creation."
    else
        cat > "$CONFIG_DIR/config.json" << EOL
{
    "default_lyrics_dir": "$DEFAULT_LYRICS_DIR",
    "file_format": "markdown",
    "add_metadata": true,
    "overwrite_existing": false,
    "quiet_mode": false
}
EOL
        print_status "Overwrote configuration file at $CONFIG_DIR/config.json"
    fi
else
    cat > "$CONFIG_DIR/config.json" << EOL
{
    "default_lyrics_dir": "$DEFAULT_LYRICS_DIR",
    "file_format": "markdown",
    "add_metadata": true,
    "overwrite_existing": false,
    "quiet_mode": false
}
EOL
    print_status "Created configuration file at $CONFIG_DIR/config.json"
fi

# Test the installation
print_info "Testing installation..."
# Give some time for PATH to propagate or ensure the script can find the executable
# This might still require a shell restart for `command -v` to work reliably in a fresh shell
sleep 1 # Small delay
if command -v lyrics-cli &> /dev/null; then
    print_status "lyrics-cli is available in PATH"
elif [[ -f "$HOME/.local/bin/lyrics-cli" ]]; then
    print_status "lyrics-cli is installed at $HOME/.local/bin/lyrics-cli"
    print_warning "You may need to restart your shell to use 'lyrics-cli' command"
else
    print_error "Installation test failed: lyrics-cli command not found after installation."
    exit 1
fi

# Final success message
echo
echo -e "${GREEN}${ROCKET} Installation completed successfully! ${ROCKET}${NC}"
echo -e "${CYAN}===============================================${NC}"
echo -e "${BLUE}Usage examples:${NC}"
echo -e "${YELLOW}  lyrics-cli search \"song title\" \"artist\"${NC}"
echo -e "${YELLOW}  lyrics-cli download \"song title\" \"artist\"${NC}"
echo -e "${YELLOW}  lyrics-cli --help${NC}"
echo
echo -e "${BLUE}Configuration:${NC}"
echo -e "${YELLOW}  Config file: $CONFIG_DIR/config.json${NC}"
echo -e "${YELLOW}  Default lyrics directory: $DEFAULT_LYRICS_DIR${NC}"
echo
echo -e "${GREEN}Happy lyric hunting! ${MUSIC_NOTE}${NC}"

# Optional: Ask if user wants to run a test
echo
echo -n "Would you like to run a quick test? (y/n): "
read -r run_test

if [[ $run_test =~ ^[Yy]$ ]]; then
    echo
    print_info "Running test..."
    
    # Try to run the command
    # Use the full path if command -v still doesn't find it immediately
    if command -v lyrics-cli &> /dev/null; then
        lyrics-cli --version 2>/dev/null || lyrics-cli --help | head -5
    else
        # Fallback to direct path, as PATH might not be updated in current shell
        "$HOME/.local/bin/lyrics-cli" --version 2>/dev/null || "$HOME/.local/bin/lyrics-cli" --help | head -5
    fi
    
    if [[ $? -eq 0 ]]; then
        print_status "Test passed! lyrics-cli is working correctly."
    else
        print_warning "Test had issues, but installation should still work."
    fi
fi

echo
echo -e "${PURPLE}Installation complete! Enjoy using lyrics-cli! ${MUSIC_NOTE}${NC}"