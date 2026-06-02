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

def process_feed(url, conn):
    print(f"Fetching feed: {url}")
    d = feedparser.parse(url)
    c = conn.cursor()
    
    fg = FeedGenerator()
    fg.id(url)
    fg.title(f"Translated: {d.feed.get('title', 'Unknown Feed')}")
    fg.link(href=url, rel='self')
    fg.description("Translated RSS feed using lightweight local pipeline.")
    
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
            
            c.execute("INSERT INTO entries (id, title, link, translated_title, translated_desc, published) VALUES (?, ?, ?, ?, ?, ?)",
                      (entry_id, title, entry.get('link', ''), trans_title, trans_desc, published))
            conn.commit()
        else:
            # Already processed
            trans_title = row[3]
            trans_desc = row[4]
            published = row[5]
            
        fe = fg.add_entry()
        fe.id(entry_id)
        fe.title(trans_title)
        fe.link(href=entry.get('link', ''))
        fe.description(trans_desc)
        # Use existing published date if parsing fails, or current time
        fe.published(published)
        
    return fg

def main():
    if not os.path.exists(FEEDS_DIR):
        os.makedirs(FEEDS_DIR)
        
    conn = init_db()
    
    # Example feed: Spanish news
    feed_url = 'http://ep00.epimg.net/rss/elpais/portada.xml'
    
    fg = process_feed(feed_url, conn)
    
    output_path = os.path.join(FEEDS_DIR, 'combined.xml')
    fg.atom_file(output_path)
    print(f"Combined Atom feed written to {output_path}")

if __name__ == "__main__":
    main()
