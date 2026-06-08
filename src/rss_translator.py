import sqlite3
import os
import time
from datetime import datetime
import feedparser
from feedgen.feed import FeedGenerator
from deep_translator import GoogleTranslator

FEEDS_DIR = os.path.join(os.path.dirname(__file__), "..", "feeds")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db.sqlite3")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (id TEXT PRIMARY KEY, title TEXT, link TEXT, translated_title TEXT, translated_desc TEXT, published TEXT)''')
    
    # Safely add fetched_at column for DB pruning (if it doesn't already exist)
    try:
        c.execute('ALTER TABLE entries ADD COLUMN fetched_at REAL')
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    return conn

def translate_text(text, target='en'):
    try:
        if not text:
            return ""
        # Handle simple translation via deep_translator
        translator = GoogleTranslator(source='auto', target=target)
        # deep_translator limits to 5000 chars
        return translator.translate(text[:4999])
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def process_feed(url, conn, fg):
    print(f"Fetching feed: {url}")
    try:
        d = feedparser.parse(url)
    except Exception as e:
        print(f"Failed to parse feed {url}: {e}")
        return
        
    c = conn.cursor()
    
    # Process entries
    for entry in d.entries:
        entry_id = entry.get('id', entry.get('link', str(time.time())))
        c.execute("SELECT title, link, translated_title, translated_desc, published FROM entries WHERE id=?", (entry_id,))
        row = c.fetchone()
        
        if row is None:
            # New entry, needs translation
            title = entry.get('title', '')
            desc = entry.get('description', '')
            print(f"Translating new entry: {title}")
            trans_title = translate_text(title)
            trans_desc = translate_text(desc)
            published = entry.get('published', datetime.now().isoformat())
            
            c.execute("INSERT INTO entries (id, title, link, translated_title, translated_desc, published, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (entry_id, title, entry.get('link', ''), trans_title, trans_desc, published, time.time()))
            conn.commit()
        else:
            # Already processed
            trans_title = row[3]
            trans_desc = row[4]
            published = row[5]
            
            # Optionally update fetched_at so active items don't get pruned
            c.execute("UPDATE entries SET fetched_at=? WHERE id=?", (time.time(), entry_id))
            conn.commit()
            
        fe = fg.add_entry()
        fe.id(entry_id)
        fe.title(trans_title)
        fe.link(href=entry.get('link', ''))
        fe.description(trans_desc)
        # Use existing published date if parsing fails, or current time
        fe.published(published)

def main():
    if not os.path.exists(FEEDS_DIR):
        os.makedirs(FEEDS_DIR)
        
    conn = init_db()
    
    # Prune database: delete items that haven't been fetched in the last 30 days
    thirty_days_ago = time.time() - (30 * 24 * 3600)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE fetched_at < ?", (thirty_days_ago,))
    conn.commit()
    
    feeds_file = os.path.join(os.path.dirname(__file__), "..", "feeds_list.txt")
    if not os.path.exists(feeds_file):
        with open(feeds_file, "w") as f:
            f.write("# List of RSS feeds to be translated and served\n")
            f.write("http://ep00.epimg.net/rss/elpais/portada.xml\n")
            
    with open(feeds_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
    fg = FeedGenerator()
    fg.id("combined-translated-feed")
    fg.title("Combined Translated Feeds")
    fg.link(href="http://localhost:8080/combined.xml", rel='self')
    fg.description("Combined and translated RSS feeds using lightweight local pipeline.")
    
    for feed_url in urls:
        process_feed(feed_url, conn, fg)
    
    output_path = os.path.join(FEEDS_DIR, 'combined.xml')
    if len(urls) > 0:
        fg.atom_file(output_path)
        print(f"Combined Atom feed written to {output_path}")
    else:
        print("No feeds processed. Add URLs to feeds_list.txt")

if __name__ == "__main__":
    main()
