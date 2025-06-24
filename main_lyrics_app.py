# main_lyrics_app.py
import re
from lyrics_api_functions import get_lyrics_from_api, save_lyrics_to_file

def main():
    """
    Main function to run the CLI application.
    """
    print("Welcome to the Python Lyrics Scraper!")
    print("Using Lyrics.ovh API for lyric fetching.")
    while True:
        song_title = input("Enter the song title (or type 'exit' to quit): ").strip()
        if song_title.lower() == 'exit':
            break

        artist = input("Enter the artist name (optional, press Enter to skip): ").strip()

        # Attempt to get lyrics from API first
        lyrics = get_lyrics_from_api(artist if artist else "", song_title) # Pass empty string if artist is not provided

        if lyrics:
            print("\n--- Lyrics ---")
            print(lyrics)
            print("--------------\n")

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
            print("Sorry, could not find lyrics for that song via API. Please try again with a different spelling or more details.")

if __name__ == "__main__":
    main()
