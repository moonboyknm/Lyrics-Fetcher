#!/usr/bin/env python3
"""
LyricsCLI - A command-line tool to search and download song lyrics.

Usage:
    lyrics-cli                    # Interactive mode
    lyrics-cli search "song name" # Search and select
    lyrics-cli get "artist" "song" # Direct download
    lyrics-cli --version          # Show version
    lyrics-cli --help            # Show help
"""

import sys
import os
import argparse
from lyrics_fetcher import LyricsFetcher, interactive_search_and_download, sanitize_filename

__version__ = "1.0.0"

def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog='lyrics-cli',
        description='🎵 Search and download song lyrics to markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lyrics-cli                           # Interactive search mode
  lyrics-cli search "bohemian rhapsody" # Search for song
  lyrics-cli get "Queen" "Bohemian Rhapsody" # Direct download
  lyrics-cli --version                 # Show version

Default output directory: /home/archboyknm/Documents/Obsidian/Lyrics/
        """
    )
    
    parser.add_argument('--version', action='version', version=f'lyrics-cli {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for songs')
    search_parser.add_argument('query', help='Song title or search query')
    search_parser.add_argument('--artist', '-a', help='Artist name hint')
    search_parser.add_argument('--output', '-o', help='Output directory')
    
    # Get command (direct download)
    get_parser = subparsers.add_parser('get', help='Download lyrics directly')
    get_parser.add_argument('artist', help='Artist name')
    get_parser.add_argument('song', help='Song title')
    get_parser.add_argument('--output', '-o', help='Output directory')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Download multiple songs from file')
    batch_parser.add_argument('file', help='File with songs (format: Artist - Song per line)')
    batch_parser.add_argument('--output', '-o', help='Output directory')
    
    args = parser.parse_args()
    
    # If no command provided, run interactive mode
    if not args.command:
        try:
            interactive_search_and_download()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        return
    
    # Handle commands
    try:
        if args.command == 'search':
            handle_search_command(args)
        elif args.command == 'get':
            handle_get_command(args)
        elif args.command == 'batch':
            handle_batch_command(args)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def handle_search_command(args):
    """Handle the search command."""
    fetcher = LyricsFetcher()
    
    print(f"🔍 Searching for: '{args.query}'")
    if args.artist:
        print(f"   Artist hint: '{args.artist}'")
    
    results = fetcher.search_songs(args.query, args.artist)
    
    if not results:
        print("❌ No songs found! Try different search terms.")
        return
    
    # Display results
    print(f"\n🎯 Found {len(results)} matches:")
    print("=" * 40)
    
    for i, result in enumerate(results, 1):
        confidence_emoji = "🎯" if result['confidence'] == 'high' else "🎲"
        print(f"{i:2d}. {confidence_emoji} {result['artist']} - {result['song']}")
    
    print(f"{len(results) + 1:2d}. ❌ None of these (exit)")
    
    # Get user choice
    try:
        choice = input(f"\nSelect song (1-{len(results) + 1}): ").strip()
        choice_num = int(choice)
        
        if choice_num == len(results) + 1:
            print("👋 Goodbye!")
            return
        
        if 1 <= choice_num <= len(results):
            selected = results[choice_num - 1]
            download_lyrics(fetcher, selected['artist'], selected['song'], args.output)
        else:
            print("❌ Invalid selection!")
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return

def handle_get_command(args):
    """Handle the get command (direct download)."""
    fetcher = LyricsFetcher()
    download_lyrics(fetcher, args.artist, args.song, args.output)

def handle_batch_command(args):
    """Handle the batch command."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return
    
    fetcher = LyricsFetcher()
    output_dir = args.output or "/home/archboyknm/Documents/Obsidian/Lyrics/"
    
    print(f"📁 Output directory: {output_dir}")
    print("📂 Processing batch file...")
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        successful = 0
        failed = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                if ' - ' in line:
                    artist, song_title = line.split(' - ', 1)
                    artist = artist.strip()
                    song_title = song_title.strip()
                else:
                    print(f"⚠️ Skipping line {i}: Invalid format '{line}'")
                    continue
                
                print(f"\n📥 Processing {i}: {artist} - {song_title}")
                
                lyrics = fetcher.get_lyrics(artist, song_title)
                if lyrics:
                    safe_song = sanitize_filename(song_title)
                    safe_artist = sanitize_filename(artist)
                    filename = f"{safe_song} - {safe_artist}.md"
                    
                    saved_path = fetcher.save_lyrics_to_file(
                        filename, lyrics, song_title, artist, output_dir
                    )
                    
                    if saved_path:
                        successful += 1
                        print(f"✅ Success: {saved_path}")
                    else:
                        failed += 1
                        print(f"❌ Failed to save: {artist} - {song_title}")
                else:
                    failed += 1
                    print(f"❌ Failed to fetch: {artist} - {song_title}")
                
                # Small delay to be respectful to the API
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing line {i}: {e}")
                failed += 1
        
        print(f"\n📊 BATCH RESULTS:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output directory: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def download_lyrics(fetcher, artist, song_title, output_dir=None):
    """Download lyrics for a specific song."""
    if not output_dir:
        output_dir = "/home/archboyknm/Documents/Obsidian/Lyrics/"
    
    print(f"📡 Downloading: {artist} - {song_title}")
    print(f"📁 Output directory: {output_dir}")
    
    lyrics = fetcher.get_lyrics(artist, song_title)
    
    if lyrics:
        # Create filename
        safe_song = sanitize_filename(song_title)
        safe_artist = sanitize_filename(artist)
        filename = f"{safe_song} - {safe_artist}.md"
        
        # Save file
        saved_path = fetcher.save_lyrics_to_file(
            filename, lyrics, song_title, artist, output_dir
        )
        
        if saved_path:
            print(f"\n🎉 SUCCESS! Lyrics saved to: {saved_path}")
            
            # Ask to open file in interactive mode
            if sys.stdin.isatty():
                try:
                    open_file = input("Open the file? (y/n): ").strip().lower()
                    if open_file in ['y', 'yes']:
                        import subprocess
                        if os.name == 'nt':  # Windows
                            os.startfile(saved_path)
                        elif os.uname().sysname == 'Darwin':  # macOS
                            subprocess.call(['open', saved_path])
                        else:  # Linux
                            subprocess.call(['xdg-open', saved_path])
                except:
                    pass
        else:
            print("❌ Failed to save lyrics file.")
    else:
        print("❌ Failed to fetch lyrics. The song might not be available.")

if __name__ == "__main__":
    main()