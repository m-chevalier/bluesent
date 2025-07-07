import json
import logging
import os
from langdetect import detect
from atproto import Client, models

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BlueskyScraper:
    def __init__(self, bluesky_handle: str, bluesky_password: str):
        self.client = Client()
        self.bluesky_handle = bluesky_handle
        self.bluesky_password = bluesky_password
        self._login()

    def _login(self):
        try:
            self.client.login(self.bluesky_handle, self.bluesky_password)
            logging.info(f"Successfully logged in as {self.bluesky_handle}")
        except Exception as e:
            logging.error(f"Failed to login to Bluesky as {self.bluesky_handle}: {e}")
            raise

    def init_keyword_list(self, file_path: str):
        """Initialize a list of keywords from a file."""
        keywords = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line:
                        keywords.append(stripped_line.lower())
            logging.info(f"Successfully loaded {len(keywords)} keywords from {file_path}")
        except FileNotFoundError:
            logging.error(f"Wordlist file not found at {file_path}. No keyword filtering will be applied.")
        except Exception as e:
            logging.error(f"Could not read wordlist file {file_path}: {e}")
        return keywords

    def _is_english_post(self, post_view) -> bool:
        """Checks if a post is likely in English."""
        if hasattr(post_view.record, 'langs') and post_view.record.langs:
            return 'en' in post_view.record.langs

        if hasattr(post_view.record, 'text') and post_view.record.text:
            try:
                detected_lang = detect(post_view.record.text)
                return detected_lang == 'en'
            except Exception as e:
                logging.warning(f"Language detection failed for post {post_view.uri}: {e}")
        return False # Default to False if language cannot be determined or text is missing


    def search_posts(self, search_term: str = None, limit: int = 10, cursor: str = None):
        logging.info(f"Searching for posts with term: '{search_term}' (limit: {limit})")
        found_posts_data = []
        seen_uris = set()
        try:
            params = models.AppBskyFeedSearchPosts.Params(
                q=search_term,
                limit=limit,
                cursor=cursor
            )
            search_results = self.client.app.bsky.feed.search_posts(
                params=params
            )

            if search_results and search_results.posts:
                for post_view in search_results.posts:
                    # Deduplicate by URI to avoid returning the same post twice within the same search
                    if post_view.uri in seen_uris:
                        continue
                    seen_uris.add(post_view.uri)

                    post_data = {
                        "uri": post_view.uri,
                        "cid": post_view.cid,
                        "created_at": post_view.record.created_at,
                        "text": post_view.record.text,
                        "langs": post_view.record.langs if hasattr(post_view.record, 'langs') else None,
                        "tags": post_view.record.tags if hasattr(post_view.record, 'tags') else None,
                        "like_count": post_view.like_count if hasattr(post_view, 'like_count') else 0,
                        "repost_count": post_view.repost_count if hasattr(post_view, 'repost_count') else 0,
                        "reply_count": post_view.reply_count if hasattr(post_view, 'reply_count') else 0,
                        "quote_count": post_view.quote_count if hasattr(post_view, 'quote_count') else 0,
                    }
                    if self._is_english_post(post_view):
                        found_posts_data.append(post_data)

            return found_posts_data, search_results.cursor
        except Exception as e:
            logging.error(f"Error searching posts for '{search_term}': {e}")
            return [], None
        

    def scrape_by_keywords(self, keywords: list[str], limit_per_keyword: int = 10):
        all_scraped_data = []
        for keyword in keywords:
            logging.info(f"Scraping for keyword: {keyword}")

            keyword_posts = []
            fetched_count = 0

            while fetched_count < limit_per_keyword:
                remaining_limit = limit_per_keyword - fetched_count
                if remaining_limit <= 0:
                    break

                # The API might have its own internal max limit per request (e.g., 100)
                # So we fetch in batches respecting that, up to remaining_limit
                batch_limit = min(remaining_limit, 100)

                posts, next_cursor = self.search_posts(
                    search_term=keyword,
                    limit=batch_limit,
                )

                if posts:
                    keyword_posts.extend(posts)
                    fetched_count += len(posts)

                if not next_cursor or not posts: # No more posts or error
                    break

            all_scraped_data.extend(keyword_posts)
        return all_scraped_data

    def save_to_json(self, data: list, filename: str = "scraped_bluesky_posts.json"):
        if not data:
            logging.info("No data to save.")
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully saved {len(data)} posts to {filename}")
        except IOError as e:
            logging.error(f"Error saving data to JSON file {filename}: {e}")



def scrape_non_keyword_posts():
    client = BlueskyScraper(
        bluesky_handle=os.environ.get("BLUESKY_HANDLE", "peepeepeepeepoo.bsky.social"),
        bluesky_password=os.environ.get("BLUESKY_APP_PASSWORD", "4k2h-ktfb-2cih-mvzo")
    )
    keywords = client.init_keyword_list("../common-words.txt")
    all_scraped_data = client.scrape_by_keywords(keywords, limit_per_keyword=10)
    client.save_to_json(all_scraped_data, "scraped_bluesky_nonllm_posts.json")

def main():
    BLUESKY_HANDLE = os.environ.get("BLUESKY_HANDLE", "peepeepeepeepoo.bsky.social")
    BLUESKY_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "4k2h-ktfb-2cih-mvzo")

    client = BlueskyScraper(
        bluesky_handle=BLUESKY_HANDLE,
        bluesky_password=BLUESKY_PASSWORD
    )
    keywords = client.init_keyword_list("training_wordlist.txt")  # Load first 10 keywords for testing
    scraped_data = client.scrape_by_keywords(keywords, limit_per_keyword=500)
    client.save_to_json(scraped_data, "scraped_bluesky_posts.json")


if __name__ == "__main__":
    scrape_non_keyword_posts()