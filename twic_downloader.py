import requests
import time
import os
from urllib.parse import urljoin
import random
import click

def download_file(url, local_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def get_last_downloaded():
    with open('last_downloaded.txt', 'r') as f:
        return int(f.read().strip())

def save_last_downloaded(number):
    with open('last_downloaded.txt', 'w') as f:
        f.write(str(number))

def try_download(url, local_filename, max_retries=3):
    for attempt in range(max_retries):
        try:
            download_file(url, local_filename)
            return True
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 10)
                click.echo(click.style(f"Attempt {attempt + 1} failed. Retrying in {wait_time:.2f} seconds...", fg='yellow'))
                time.sleep(wait_time)
            else:
                click.echo(click.style(f"Error downloading after {max_retries} attempts: {e}", fg='red'))
                return False

@click.command()
@click.option('--start', '-s', 'start_number', type=int, help='Starting TWIC number')
@click.option('--end', '-e', 'end_number', type=int, help='Ending TWIC number (optional)')
def main(start_number, end_number):
    """Download chess game archives from The Week in Chess (TWIC)."""
    base_url = "https://theweekinchess.com/zips/"

    # If start_number is not provided, use the last downloaded number + 1
    if start_number is None:
        last_downloaded = get_last_downloaded()
        start_number = last_downloaded + 1
        click.echo(f"Starting from number {start_number} (based on last downloaded)")

    current_number = start_number

    # Create a directory to store the downloaded files
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    while True:
        if end_number and current_number > end_number:
            click.echo("Reached specified end number. Stopping.")
            break

        filename = f"twic{current_number}c6.zip"
        url = urljoin(base_url, filename)
        local_filename = os.path.join("downloads", filename)

        click.echo(f"Attempting to download {url}...")

        if try_download(url, local_filename):
            click.echo(click.style(f"Successfully downloaded {filename}", fg='green'))
            save_last_downloaded(current_number)
        else:
            click.echo(click.style(
                f"Failed to download {filename} after 3 attempts. This is likely the end of available files.",
                fg='yellow'
            ))
            break  # Exit immediately after first complete failure

        # Implement waiting strategy
        wait_time = random.uniform(3, 7)  # Random wait between 3 to 7 seconds
        click.echo(f"Waiting for {wait_time:.2f} seconds before next download...")
        time.sleep(wait_time)

        current_number += 1

    click.echo(click.style(f"Download complete. Last successful download: {get_last_downloaded()}", fg='green'))

if __name__ == "__main__":
    main()
