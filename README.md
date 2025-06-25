# 🎵 Lyrics-Fetcher

A powerful command-line tool for searching and downloading song lyrics directly to your local filesystem, with special support for Obsidian note-taking workflows.

## ✨ Features

- 🔍 **Search lyrics** by song title and artist
- 📥 **Download lyrics** in multiple formats (Markdown, plain text)
- 📁 **Organized storage** with automatic folder structure
- 🏷️ **Metadata support** including artist, album, and song information
- ⚙️ **Configurable** with JSON configuration file
- 🗂️ **Obsidian integration** - perfect for your music notes vault
- 🎨 **Beautiful CLI interface** with colors and emojis
- 🔒 **Safe installation** - no root privileges required
- ⚠️ **The API can be problematic sometimes**

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Internet connection for fetching lyrics

### Installation

1. **Clone or download the project:**
   ```bash
   git clone https://github.com/moonboyknm/Lyrics-Fetcher
   cd Lyrics-Fetcher/
   ```

2. **Run the installer:**
   ```bash
   bash install.sh
   ```

3. **Follow the prompts** - the installer will:
   - Check dependencies
   - Install required Python packages
   - Set up the executable
   - Configure your PATH (optional)
   - Create default directories

4. **Restart your shell** or run:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

## 📖 Usage

### Basic Commands

```bash
# Search for lyrics
lyrics-cli search "Bohemian Rhapsody" "Queen"

# Download lyrics to default directory
lyrics-cli download "Imagine" "John Lennon"

# Download to specific directory
lyrics-cli download "Hotel California" "Eagles" --output ~/Music/Lyrics

# Show help
lyrics-cli --help

# Show version
lyrics-cli --version
```

### Advanced Usage

```bash
# Download with custom filename
lyrics-cli download "Stairway to Heaven" "Led Zeppelin" --filename "stairway.md"

# Skip metadata in output
lyrics-cli download "Yesterday" "The Beatles" --no-metadata

# Overwrite existing files
lyrics-cli download "Hey Jude" "The Beatles" --overwrite

# Quiet mode (minimal output)
lyrics-cli download "Let It Be" "The Beatles" --quiet

# Export as plain text instead of Markdown
lyrics-cli download "Come Together" "The Beatles" --format txt
```

## ⚙️ Configuration

The configuration file is located at `~/.config/lyrics-cli/config.json`:

```json
{
    "default_lyrics_dir": "~/Documents/Obsidian/Lyrics",
    "file_format": "markdown",
    "add_metadata": true,
    "overwrite_existing": false,
    "quiet_mode": false
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `default_lyrics_dir` | Default directory for saving lyrics | `~/Documents/Obsidian/Lyrics` |
| `file_format` | Output format (`markdown` or `txt`) | `markdown` |
| `add_metadata` | Include song metadata in output | `true` |
| `overwrite_existing` | Overwrite existing files | `false` |
| `quiet_mode` | Minimal console output | `false` |

## 📁 File Organization

Lyrics are automatically organized in a clean folder structure:

```
~/Documents/Obsidian/Lyrics/
├── Queen/
│   ├── Bohemian Rhapsody.md
│   └── We Will Rock You.md
├── The Beatles/
│   ├── Hey Jude.md
│   ├── Let It Be.md
│   └── Yesterday.md
└── Led Zeppelin/
    └── Stairway to Heaven.md
```

## 📝 Output Format

### Markdown Format (default)
```markdown
# Song Title
**Artist:** Artist Name
**Album:** Album Name (if available)
**Year:** Release Year (if available)

---

[Verse 1]
Lyrics content here...

[Chorus]
More lyrics...
```

### Plain Text Format
```
Song Title
Artist: Artist Name
Album: Album Name
Year: Release Year

[Verse 1]
Lyrics content here...

[Chorus]
More lyrics...
```

## 🔧 Command Line Options

```
Usage: lyrics-cli [COMMAND] [OPTIONS] <song> <artist>

Commands:
  search              Search for lyrics without downloading
  download            Download lyrics to file

Options:
  -o, --output DIR    Output directory (overrides config)
  -f, --filename STR  Custom filename
  --format FORMAT     Output format: markdown, txt
  --overwrite         Overwrite existing files
  --no-metadata       Skip metadata in output
  --quiet             Quiet mode - minimal output
  -h, --help          Show this help message
  -v, --version       Show version information
```

## 🐛 Troubleshooting

### Common Issues

**"Command not found: lyrics-cli"**
- Make sure `~/.local/bin` is in your PATH
- Try running the installer again
- Restart your shell: `source ~/.bashrc` or `source ~/.zshrc`

**"Permission denied"**
- Don't run the installer as root
- Check file permissions: `ls -la ~/.local/bin/lyrics-cli`
- Try: `chmod +x ~/.local/bin/lyrics-cli`

**"No lyrics found"**
- Check your internet connection
- Try different search terms
- Some songs might not be available in the lyrics database

**"Python module not found"**
- Reinstall dependencies: `pip3 install --user requests`
- Check Python installation: `python3 --version`

### Manual Installation

If the automatic installer doesn't work:

1. **Install dependencies:**
   ```bash
   pip3 install --user requests
   ```

2. **Copy files manually:**
   ```bash
   mkdir -p ~/.local/bin
   cp lyrics_fetcher.py ~/.local/bin/
   cp main.py ~/.local/bin/lyrics-cli
   chmod +x ~/.local/bin/lyrics-cli
   ```

3. **Add to PATH:**
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Development Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd lyrics-cli

# Install in development mode
pip3 install --user -e .

# Run tests
python3 -m pytest tests/
```

## 📋 Project Structure

```
lyrics-cli/
├── main.py              # Main CLI application
├── lyrics_fetcher.py    # Core lyrics fetching logic
├── install.sh          # Installation script
├── setup.py            # Python package setup
├── README.md           # This file
├── requirements.txt    # Python dependencies
└── tests/             # Unit tests
    └── test_lyrics.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to the lyrics API providers
- Inspired by the need for better music note-taking workflows
- Built with ❤️ for the command-line and Obsidian communities

## 🔗 Links

- [Report Issues](https://github.com/moonboyknm/Lyrics-Fetcher/issues)
- [Feature Requests](https://github.com/moonboyknm/Lyrics-Fetcher/issues)
- [Obsidian](https://obsidian.md/) - The knowledge management app this tool integrates with

---

**Happy lyric hunting! 🎵**
