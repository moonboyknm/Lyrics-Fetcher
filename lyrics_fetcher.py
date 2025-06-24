import requests
import re
import os
import time
from urllib.parse import quote
import json

class LyricsFetcher:
    def __init__(self):
        # We'll use multiple APIs for better coverage
        self.apis = {
            'lyrics_ovh': 'https://api.lyrics.ovh/v1',
            'musixmatch_alt': 'https://apic-desktop.musixmatch.com/ws/1.1'
        }
        
    def search_songs(self, query, artist=None):
        """
        Search for songs using multiple methods and return a list of matches.
        """
        print(f"🔍 Searching for: '{query}'")
        if artist:
            print(f"   Artist hint: '{artist}'")
        
        results = []
        
        # Method 1: Try direct search with lyrics.ovh variations
        results.extend(self._search_lyrics_ovh_variations(query, artist))
        
        # Method 2: Try common song variations
        results.extend(self._search_common_variations(query, artist))
        
        # Remove duplicates and return
        unique_results = self._remove_duplicates(results)
        return unique_results[:10]  # Limit to top 10 results
    
    def _search_lyrics_ovh_variations(self, query, artist=None):
        """
        Search using different artist/song combinations.
        """
        results = []
        search_combinations = []
        
        if artist:
            # If artist is provided, try exact combination
            search_combinations.append((artist, query))
            # Try swapped (in case user mixed up artist/song)
            search_combinations.append((query, artist))
        else:
            # Try to split query to guess artist and song
            if ' - ' in query:
                parts = query.split(' - ', 1)
                search_combinations.append((parts[0].strip(), parts[1].strip()))
                search_combinations.append((parts[1].strip(), parts[0].strip()))
            elif ' by ' in query.lower():
                parts = query.lower().split(' by ', 1)
                search_combinations.append((parts[1].strip(), parts[0].strip()))
        
        # Try each combination
        for test_artist, test_song in search_combinations:
            if self._test_lyrics_availability(test_artist, test_song):
                results.append({
                    'artist': test_artist,
                    'song': test_song,
                    'confidence': 'high',
                    'source': 'lyrics.ovh'
                })
        
        return results
    
    def _search_common_variations(self, query, artist=None):
        """
        Try common artist names with the query as song title.
        """
        results = []
        
        # Common artist names to try if no artist provided
        common_artists = [
            'Taylor Swift', 'Ed Sheeran', 'Drake', 'Adele', 'Post Malone',
            'Billie Eilish', 'Ariana Grande', 'The Weeknd', 'Justin Bieber',
            'Harry Styles', 'Dua Lipa', 'Olivia Rodrigo', 'Bad Bunny'
        ]
        
        if not artist:
            # Try with popular artists
            for test_artist in common_artists[:5]:  # Limit to avoid too many requests
                if self._test_lyrics_availability(test_artist, query):
                    results.append({
                        'artist': test_artist,
                        'song': query,
                        'confidence': 'medium',
                        'source': 'lyrics.ovh'
                    })
        
        return results
    
    def _test_lyrics_availability(self, artist, song_title):
        """
        Quick test to see if lyrics are available for this artist/song combination.
        """
        try:
            clean_artist = quote(artist.strip())
            clean_song = quote(song_title.strip())
            
            api_url = f"{self.apis['lyrics_ovh']}/{clean_artist}/{clean_song}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(api_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return 'lyrics' in data and data['lyrics'] and len(data['lyrics'].strip()) > 10
            
            return False
            
        except Exception:
            return False
    
    def _remove_duplicates(self, results):
        """
        Remove duplicate results based on artist and song combination.
        """
        seen = set()
        unique_results = []
        
        for result in results:
            key = (result['artist'].lower(), result['song'].lower())
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def get_lyrics(self, artist, song_title):
        """
        Fetch lyrics for a specific artist and song.
        """
        try:
            clean_artist = quote(artist.strip())
            clean_song = quote(song_title.strip())
            
            api_url = f"{self.apis['lyrics_ovh']}/{clean_artist}/{clean_song}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            print(f"📡 Fetching lyrics for: {artist} - {song_title}")
            
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'lyrics' in data and data['lyrics']:
                    lyrics = data['lyrics'].strip()
                    # Clean up excessive newlines
                    lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
                    return lyrics
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching lyrics: {e}")
            return None
    
    def save_lyrics_to_file(self, filename, lyrics_text, song_title, artist, output_dir=None):
        """
        Save lyrics to a markdown file.
        """
        if output_dir is None:
            output_dir = "/home/archboyknm/Documents/Obsidian/Lyrics/"
        
        try:
            # Ensure .md extension
            if not filename.lower().endswith('.md'):
                filename += '.md'
            
            # Create full path
            full_path = os.path.join(output_dir, filename)
            
            # Create directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# {song_title}\n")
                f.write(f"**Artist:** {artist}\n\n")
                f.write("---\n\n")
                
                # Write lyrics
                f.write(lyrics_text)
                f.write("\n\n")
                f.write("---\n")
                f.write(f"\n*Fetched using Lyrics API*\n")
            
            print(f"✅ Lyrics saved to: {full_path}")
            return full_path
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None

def sanitize_filename(filename):
    """
    Remove or replace characters that are invalid in filenames.
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace spaces with spaces (keep readable), limit length
    filename = filename[:100]  # Limit length
    
    return filename.strip()

def interactive_search_and_download():
    """
    Interactive function to search and download lyrics.
    """
    fetcher = LyricsFetcher()
    
    print("🎵 LYRICS SEARCH & DOWNLOAD 🎵")
    print("=" * 40)
    
    # Get search query
    query = input("Enter song title (or 'Artist - Song'): ").strip()
    if not query:
        print("❌ Search query cannot be empty!")
        return
    
    artist_hint = input("Enter artist name (optional, press Enter to skip): ").strip()
    artist_hint = artist_hint if artist_hint else None
    
    # Search for songs
    print(f"\n{'='*40}")
    results = fetcher.search_songs(query, artist_hint)
    
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
            
            # Fetch and save lyrics
            lyrics = fetcher.get_lyrics(selected['artist'], selected['song'])
            
            if lyrics:
                # Create filename
                safe_song = sanitize_filename(selected['song'])
                safe_artist = sanitize_filename(selected['artist'])
                filename = f"{safe_song} - {safe_artist}.md"
                
                # Get output directory
                default_dir = "/home/archboyknm/Documents/Obsidian/Lyrics/"
                print(f"\nDefault directory: {default_dir}")
                custom_dir = input("Custom output directory (press Enter for default): ").strip()
                output_dir = custom_dir if custom_dir else default_dir
                
                # Save file
                saved_path = fetcher.save_lyrics_to_file(
                    filename, lyrics, selected['song'], selected['artist'], output_dir
                )
                
                if saved_path:
                    print(f"\n🎉 SUCCESS! Lyrics downloaded!")
                    
                    # Ask to open file
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
        else:
            print("❌ Invalid selection!")
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return