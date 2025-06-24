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
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed. Installing git..."
    if command -v pacman &> /dev/null; then
        sudo pacman -S git --noconfirm
    else
        print_error "Please install git manually and run this script again."
        exit 1
    fi
fi

# Create default lyrics directory
DEFAULT_LYRICS_DIR="$HOME/Documents/Obsidian/Lyrics"
print_info "Creating default lyrics directory..."
mkdir -p "$DEFAULT_LYRICS_DIR"
print_status "Created directory: $DEFAULT_LYRICS_DIR"

# Install the package
print_info "Installing lyrics-cli..."

# Method 1: If we're in the project directory, install from source
if [[ -f "setup.py" && -f "lyrics_fetcher.py" && -f "main.py" ]]; then
    print_info "Installing from source..."
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip3 install --user requests
    
    # Install the package in development mode
    pip3 install --user -e .
    
    if [[ $? -eq 0 ]]; then
        print_status "Successfully installed lyrics-cli from source!"
    else
        print_error "Failed to install from source"
        exit 1
    fi
    
else
    # Method 2: Install individual files to a local directory
    print_info "Installing as standalone scripts..."
    
    # Create local bin directory
    LOCAL_BIN="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN"
    
    # Copy files
    cp lyrics_fetcher.py "$LOCAL_BIN/"
    cp main.py "$LOCAL_BIN/lyrics-cli"
    
    # Make executable
    chmod +x "$LOCAL_BIN/lyrics-cli"
    
    # Install dependencies
    pip3 install --user requests
    
    print_status "Installed lyrics-cli to $LOCAL_BIN"
fi

# Check if ~/.local/bin is in PATH
print_info "Checking PATH configuration..."
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "~/.local/bin is not in your PATH"
    echo
    echo "To use lyrics-cli from anywhere, add this line to your shell config:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
    echo
    echo "Then restart your shell or run:"
    echo "  source ~/.bashrc  # or ~/.zshrc"
    echo
    
    # Ask if user wants to add to PATH automatically
    echo -n "Would you like to add ~/.local/bin to your PATH automatically? (y/n): "
    read -r add_to_path
    
    if [[ $add_to_path =~ ^[Yy]$ ]]; then
        # Detect shell and add to appropriate config
        if [[ -n "$ZSH_VERSION" ]]; then
            # User is running zsh
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            print_status "Added to ~/.zshrc"
        elif [[ -n "$BASH_VERSION" ]]; then
            # User is running bash
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_status "Added to ~/.bashrc"
        else
            # Try to detect based on available config files
            if [[ -f ~/.zshrc ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
                print_status "Added to ~/.zshrc"
            elif [[ -f ~/.bashrc ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
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

# Test the installation
print_info "Testing installation..."
if command -v lyrics-cli &> /dev/null; then
    print_status "lyrics-cli is available in PATH"
elif [[ -f "$HOME/.local/bin/lyrics-cli" ]]; then
    print_status "lyrics-cli is installed at $HOME/.local/bin/lyrics-cli"
    print_warning "You may need to restart your shell to use 'lyrics-cli' command"
else
    print_error "Installation test failed"
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
    if command -v lyrics-cli &> /dev/null; then
        lyrics-cli --version 2>/dev/null || lyrics-cli --help | head -5
    else
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