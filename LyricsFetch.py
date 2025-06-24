import requests
from bs4 import BeautifulSoup
import re
import os
import time # Import time for potential delays

def search_song(song_title, artist=None):
    """
    Searches for a song on Musixmatch using Google Search and returns the URL of the best match.
    """
    google_search_base_url = "https://www.google.com/search?q="
    search_query = f"site:musixmatch.com {song_title}"
    if artist:
        search_query += f" {artist}"

    encoded_search_query = requests.utils.quote(search_query)
    google_search_url = f"{google_search_base_url}{encoded_search_query}"

    print(f"Searching Google for '{search_query}' to find lyrics on Musixmatch...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }

    try:
        response = requests.get(google_search_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Google Search: {e}")
        print(f"Please check your internet connection.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    lyrics_url = None
    best_score = -1
    found_candidates = []

    # Strategy 1: Look for div elements commonly containing main search results,
    # and extract direct links (starting with http/https) from them.
    # 'div.g' is a very common container for a search result block.
    # Inside 'div.g', the actual clickable link is often within a 'div' with class 'yuRUbf'
    # or sometimes directly under a 'div' with class 'rc'.

    # First, try to find direct external links within known result containers
    for g_div in soup.find_all('div', class_='g'):
        # Look for the <a> tag that contains the main external link
        link_tag = g_div.find('a', href=re.compile(r'https?://')) # Direct http/https links
        title_tag = g_div.find('h3') # Get the title of the search result

        if link_tag and title_tag:
            decoded_url = link_tag['href']
            
            # Filter for Musixmatch lyrics pages
            if 'musixmatch.com/lyrics/' in decoded_url:
                link_title_text = title_tag.get_text().lower()
                
                score = 0
                normalized_song_title = song_title.lower()
                normalized_artist = artist.lower() if artist else ""

                if normalized_song_title in link_title_text or normalized_song_title.replace(" ", "-") in decoded_url.lower():
                    score += 5

                if normalized_artist and (normalized_artist in link_title_text or normalized_artist.replace(" ", "-") in decoded_url.lower()):
                    score += 3
                
                if "lyrics" in link_title_text or "lyrics" in decoded_url.lower():
                    score += 1
                
                found_candidates.append({'url': decoded_url, 'score': score, 'title': link_title_text})
                print(f"  Candidate (Direct Link): Title='{link_title_text}', URL='{decoded_url}', Score={score}")

    # Strategy 2: Fallback to /url?q= pattern if no direct links found or for other structures
    if not found_candidates:
        print("No direct Musixmatch links found in common Google result blocks. Falling back to /url?q= pattern.")
        all_potential_links = soup.find_all('a', href=re.compile(r'^/url\?q='))

        for link_tag in all_potential_links:
            href = link_tag['href']
            actual_url_match = re.search(r'/url\?q=(.*?)(?=&|$)', href)
            
            if actual_url_match:
                decoded_url = requests.utils.unquote(actual_url_match.group(1))

                if 'musixmatch.com/lyrics/' in decoded_url:
                    # For these, the title might not be in an h3, but the link text itself
                    # Try to find an h3 first, otherwise use the link's text
                    title_tag_in_link = link_tag.find('h3')
                    link_title_text = title_tag_in_link.get_text().lower() if title_tag_in_link else link_tag.get_text().lower()
                    
                    score = 0
                    normalized_song_title = song_title.lower()
                    normalized_artist = artist.lower() if artist else ""

                    if normalized_song_title in link_title_text or normalized_song_title.replace(" ", "-") in decoded_url.lower():
                        score += 5

                    if normalized_artist and (normalized_artist in link_title_text or normalized_artist.replace(" ", "-") in decoded_url.lower()):
                        score += 3
                    
                    if "lyrics" in link_title_text or "lyrics" in decoded_url.lower():
                        score += 1
                    
                    found_candidates.append({'url': decoded_url, 'score': score, 'title': link_title_text})
                    print(f"  Candidate (Fallback /url?q=): Title='{link_title_text}', URL='{decoded_url}', Score={score}")

    # Sort candidates by score and pick the best one
    if found_candidates:
        found_candidates.sort(key=lambda x: x['score'], reverse=True)
        lyrics_url = found_candidates[0]['url']
        print(f"Best matching lyrics URL found via Google: {lyrics_url}")
        return lyrics_url
    else:
        print("No suitable Musixmatch link found in Google search results after detailed parsing attempts.")
        return None


def get_lyrics(lyrics_url):
    """
    Scrapes lyrics from the given Musixmatch URL.
    """
    print(f"Retrieving lyrics from: {lyrics_url}")
    # Headers to mimic a browser for Musixmatch
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.musixmatch.com/', # Referer from Musixmatch's main page
        'DNT': '1',
    }
    try:
        response = requests.get(lyrics_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving lyrics from Musixmatch: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    lyrics_text = "Lyrics not found."

    # Musixmatch lyrics are often in <span class="lyrics__content__ok"> or similar.
    # It's usually within a div with a specific class for the entire lyrics section.
    # Let's target the main lyrics container elements.
    
    # Try finding the primary lyric elements
    # Musixmatch uses elements like <span class="lyrics__content__ok"> for lyric lines
    lyrics_lines = soup.find_all('span', class_=re.compile(r'lyrics__content'))
    
    if lyrics_lines:
        extracted_lines = []
        for line in lyrics_lines:
            # Get text from each line. Use .text to get visible text, strip whitespace.
            text = line.get_text().strip()
            if text: # Only add non-empty lines
                extracted_lines.append(text)
        
        if extracted_lines:
            lyrics_text = "\n".join(extracted_lines)
            # Clean up common artifacts (like trailing numbers from verse numbering, extra newlines)
            lyrics_text = re.sub(r'\n{3,}', '\n\n', lyrics_text) # Reduce multiple newlines
            lyrics_text = re.sub(r'\[.*?\]', '', lyrics_text)  # Remove things like [Verse 1], [Chorus] etc.
            lyrics_text = lyrics_text.strip()
            return lyrics_text

    print("Could not find lyrics content on the Musixmatch page. The structure might have changed.")
    return lyrics_text


def save_lyrics_to_file(filename, lyrics_text, song_title, artist=None):
    """
    Saves the given lyrics text to a Markdown file.
    Adds song title and artist (if provided) as a Markdown heading.
    """
    try:
        if not filename.lower().endswith('.md'):
            filename += '.md'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Lyrics for {song_title}")
            if artist:
                f.write(f" by {artist}")
            f.write("\n\n")

            f.write(lyrics_text)
            f.write("\n")
        print(f"Lyrics saved successfully to '{filename}'")
    except IOError as e:
        print(f"Error saving lyrics to file '{filename}': {e}")

def main():
    """
    Main function to run the CLI application.
    """
    print("Welcome to the Python Lyrics Scraper!")
    while True:
        song_title = input("Enter the song title (or type 'exit' to quit): ").strip()
        if song_title.lower() == 'exit':
            break

        artist = input("Enter the artist name (optional, press Enter to skip): ").strip()

        lyrics_url = search_song(song_title, artist if artist else None)

        if lyrics_url:
            time.sleep(1) # Small delay before hitting the lyrics page directly
            lyrics = get_lyrics(lyrics_url)
            print("\n--- Lyrics ---")
            print(lyrics)
            print("--------------\n")

            if lyrics != "Lyrics not found.":
                save_option = input("Do you want to save these lyrics to a file? (yes/no): ").strip().lower()
                if save_option == 'yes':
                    # Sanitize song title for a valid filename
                    default_filename = re.sub(r'[\\/:*?"<>|]', '', song_title).strip()
                    if artist:
                        default_filename = f"{default_filename} - {re.sub(r'[\\/:*?"<>|]', '', artist).strip()}"
                    default_filename = f"{default_filename}.md"

                    filename = input(f"Enter filename (e.g., '{default_filename}'): ").strip()
                    if not filename:
                        filename = default_filename
                    save_lyrics_to_file(filename, lyrics, song_title, artist if artist else None)
        else:
            print("Sorry, could not find lyrics for that song. Please try again with a different spelling or more details.")

if __name__ == "__main__":
    main()
