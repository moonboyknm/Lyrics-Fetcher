import requests
import re
import os
import time
from bs4 import BeautifulSoup

def get_lyrics_from_api(artist, song_title):
    """
    Fetches lyrics from the Lyrics.ovh API.
    """
    api_url = f"https://api.lyrics.ovh/v1/{artist}/{song_title}"
    print(f"Attempting to fetch lyrics from Lyrics.ovh API: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if 'lyrics' in data:
            lyrics = data['lyrics'].strip()
            if lyrics: # Ensure lyrics are not empty
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics) # Reduce multiple newlines
                return lyrics
            else:
                print("API returned empty lyrics.")
                return None
        elif 'error' in data:
            print(f"API Error: {data['error']}")
            return None
        else:
            print("API response did not contain 'lyrics' key.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching lyrics from API: {e}")
        return None
    except ValueError: # Catches JSONDecodeError if response is not valid JSON
        print(f"API response was not valid JSON for {artist} - {song_title}.")
        return None


def search_song(song_title, artist=None):
    """
    Searches for a song on Musixmatch using Google Search and returns the URL of the best match.
    This function is kept for reference but is not directly used for lyric fetching with the API.
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

    for g_div in soup.find_all('div', class_='g'):
        link_tag = g_div.find('a', href=re.compile(r'https?://'))
        title_tag = g_div.find('h3')

        if link_tag and title_tag:
            decoded_url = link_tag['href']
            
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

    if not found_candidates:
        all_potential_links = soup.find_all('a', href=re.compile(r'^/url\?q='))

        for link_tag in all_potential_links:
            href = link_tag['href']
            actual_url_match = re.search(r'/url\?q=(.*?)(?=&|$)', href)
            
            if actual_url_match:
                decoded_url = requests.utils.unquote(actual_url_match.group(1))

                if 'musixmatch.com/lyrics/' in decoded_url:
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

    if found_candidates:
        found_candidates.sort(key=lambda x: x['score'], reverse=True)
        lyrics_url = found_candidates[0]['url']
        print(f"Best matching lyrics URL found via Google: {lyrics_url}")
        return lyrics_url
    else:
        print("No suitable Musixmatch link found in Google search results after detailed parsing attempts.")
        return None

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
 