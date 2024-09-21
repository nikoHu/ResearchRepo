import csv
import os
import time
import requests
from urllib.parse import urlparse
import json
from datetime import datetime

class GitHubRepoDownloader:
    def __init__(self, csv_file, download_dir, tokens, proxies=None, max_retries=3, retry_delay=5):
        self.csv_file = csv_file
        self.download_dir = download_dir
        self.tokens = tokens
        self.current_token_index = 0
        self.proxies = proxies
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = self.get_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        if self.proxies:
            self.session.proxies.update(self.proxies)
        self.failed_downloads = []
        self.progress_file = f"{os.path.splitext(csv_file)[0]}_progress.json"

    def get_headers(self):
        return {
            "Authorization": f"token {self.tokens[self.current_token_index]}",
            "Accept": "application/vnd.github.v3+json",
        }

    def rotate_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
        self.headers = self.get_headers()
        self.session.headers.update(self.headers)

    def get_repo_info(self, url):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            owner, repo = path_parts[:2]
            return owner, repo
        return None, None

    def download_repo(self, url, category):
        owner, repo = self.get_repo_info(url)
        if not owner or not repo:
            print(f"Invalid URL: {url}")
            return False

        api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(api_url, stream=True, timeout=30)
                response.raise_for_status()

                category_dir = os.path.join(self.download_dir, category)
                os.makedirs(category_dir, exist_ok=True)
                filename = f"{owner}_{repo}.zip"
                filepath = os.path.join(category_dir, filename)

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Downloaded: {filename}")
                return True
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed to download: {url}. Error: {str(e)}")
                if "rate limit exceeded" in str(e).lower():
                    print("Rate limit exceeded. Rotating token.")
                    self.rotate_token()
                time.sleep(self.retry_delay)
        
        print(f"Failed to download after {self.max_retries} attempts: {url}")
        self.failed_downloads.append({"url": url, "category": category})
        return False

    def save_progress(self, processed_count):
        progress = {
            "processed_count": processed_count,
            "failed_downloads": self.failed_downloads,
            "last_update": datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            return progress.get("processed_count", 0), progress.get("failed_downloads", [])
        return 0, []

    def process_csv(self):
        total_repos = 0
        downloaded_repos = 0
        processed_count, self.failed_downloads = self.load_progress()

        with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            total_repos = len(rows)

            for i, row in enumerate(rows[processed_count:], start=processed_count):
                url = row['url']
                category = os.path.splitext(os.path.basename(self.csv_file))[0].split('_')[0]
                if self.download_repo(url, category):
                    downloaded_repos += 1
                self.save_progress(i + 1)
                time.sleep(1)  # Add a delay to avoid hitting rate limits

        print(f"Total repositories: {total_repos}")
        print(f"Successfully downloaded: {downloaded_repos}")
        print(f"Failed downloads: {len(self.failed_downloads)}")

        if self.failed_downloads:
            failed_file = f"{os.path.splitext(self.csv_file)[0]}_failed_downloads.json"
            with open(failed_file, 'w') as f:
                json.dump(self.failed_downloads, f, indent=2)
            print(f"Failed downloads saved to: {failed_file}")

if __name__ == "__main__":
    csv_files = ["android_projects.csv", "network_projects.csv", "database_projects.csv"]
    download_dir = "downloaded_repos"
    github_tokens = [
        "xxxx",
        # Add more tokens here
    ]

    # 设置代理
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "https://127.0.0.1:10809"
    }

    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        downloader = GitHubRepoDownloader(csv_file, download_dir, github_tokens, proxies=proxies)
        downloader.process_csv()
        print(f"Finished processing {csv_file}")
        print("---")

    print("All downloads completed.")