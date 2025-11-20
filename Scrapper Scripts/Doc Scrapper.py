import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# ==================== EASILY EDITABLE CONFIGURATION ====================

# Target directory where PDFs will be saved
TARGET_DIR = r"C:\Users\user\Desktop\Python Course\SQL, Pyth, and PostGres Docs"

# Maximum number of documents to download
MAX_DOWNLOADS = 20

# Keywords that PDFs MUST contain (update here to change search criteria)
REQUIRED_KEYWORDS = ['sql', 'python', 'postgres']

# Keywords to search for in sources (add or remove keywords here)
SEARCH_KEYWORDS = [
    'sql', 'python', 'postgresql', 'postgres'
]

# ==================== SCRAPE SOURCES - EASILY UPDATE URLs HERE ====================
# Format: {name, base_url, search_templates}
# Just paste new URLs below to add new sources!

SEARCH_SOURCES = [
    {
        'name': 'PDFDrive (webs.nf)',
        'base_url': 'https://pdfdrive.webs.nf/',
        'search_templates': ['?s={keyword}', '/search?q={keyword}'],
        'enabled': True
    },
    {
        'name': 'PDFDrive (com.co)',
        'base_url': 'https://pdfdrive.com.co/',
        'search_templates': ['?s={keyword}', '/search?q={keyword}'],
        'enabled': True
    },
    {
        'name': 'BookBoon',
        'base_url': 'https://www.bookboon.com/en/textbooks/',
        'search_templates': ['{keyword}'],
        'enabled': True
    }
]

# Direct source URLs (pages to scrape for PDF links)
# Just paste URLs here to add new sources!
DIRECT_SOURCES = [
    {
        'name': 'BookBoon - IT Books',
        'url': 'https://www.bookboon.com/en/textbooks/it',
        'enabled': True
    },
    {
        'name': 'Open Textbooks - Databases',
        'url': 'https://open.umn.edu/opentextbooks/subjects/databases',
        'enabled': True
    }
]

# ==================== END OF CONFIGURATION ====================

# Create target directory
os.makedirs(TARGET_DIR, exist_ok=True)

print("🔍 Starting Web Scraper for SQL, Python, and PostgreSQL Documents...")
print(f"📁 Target directory: {TARGET_DIR}\n")

# ==================== SCRAPER CLASS ====================

class PDFScraper:
    """Main scraper class for downloading PDFs with configurable sources"""
    
    def __init__(self):
        self.documents = []
        self.downloaded_count = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    # ==================== VALIDATION METHODS ====================
    
    def is_valid_pdf_url(self, url):
        """Check if URL is a valid PDF link"""
        return url and '.pdf' in url.lower() and 'javascript' not in url.lower()
    
    def has_required_keywords(self, title):
        """Check if title contains required keywords"""
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in REQUIRED_KEYWORDS)
    
    def is_duplicate(self, url):
        """Check if document already exists in list"""
        return any(doc['url'] == url for doc in self.documents)
    
    def file_exists(self, filename):
        """Check if file already downloaded"""
        return os.path.exists(os.path.join(TARGET_DIR, filename))
    
    # ==================== DOWNLOAD METHODS ====================
    
    def download_file(self, url, filename):
        """Download a file from URL and save it"""
        try:
            print(f"   ⬇️  Downloading: {filename}...", end=" ")
            
            response = self.session.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(TARGET_DIR, filename)
            
            # Write file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✅ ({file_size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
            # Clean up failed download
            try:
                os.remove(os.path.join(TARGET_DIR, filename))
            except:
                pass
            return False
    
    def try_download_document(self, title, url):
        """Attempt to download a document"""
        try:
            # Clean filename
            clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{clean_title[:60]}.pdf"
            
            # Check if file already exists
            if self.file_exists(filename):
                print(f"   ⏭️  {filename} (already exists)")
                return False
            
            return self.download_file(url, filename)
        
        except Exception as e:
            print(f"   ❌ Error preparing download for {title}: {str(e)[:40]}")
            return False
    
    # ==================== SCRAPING METHODS ====================
    
    def scrape_search_sources(self):
        """Scrape from all configured search sources"""
        for source in SEARCH_SOURCES:
            if not source['enabled'] or self.downloaded_count >= MAX_DOWNLOADS:
                continue
            
            print(f"🌐 Scraping {source['name']}...")
            
            # Special handling for Welib
            if 'welib' in source['base_url'].lower():
                self._scrape_welib()
                continue
            
            for keyword in SEARCH_KEYWORDS:
                if self.downloaded_count >= MAX_DOWNLOADS:
                    break
                
                for template in source['search_templates']:
                    if self.downloaded_count >= MAX_DOWNLOADS:
                        break
                    
                    search_url = source['base_url'] + template.format(keyword=keyword)
                    self._process_search_results(search_url, source['name'])
    
    def _scrape_welib(self):
        """Special scraper for welib.org - fetches PDF list from their catalog"""
        try:
            # Try to access welib's books/resources page
            base_urls = [
                'https://welib.org/',
                'https://welib.org/books/',
                'https://welib.org/resources/'
            ]
            
            for base_url in base_urls:
                if self.downloaded_count >= MAX_DOWNLOADS:
                    return
                
                try:
                    response = self.session.get(base_url, timeout=15)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for all links that might contain PDFs
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        if self.downloaded_count >= MAX_DOWNLOADS:
                            return
                        
                        href = link.get('href')
                        title = link.get_text(strip=True)
                        
                        # Check if link contains keywords and points to a downloadable resource
                        has_keywords = any(kw in title.lower() or kw in href.lower() for kw in REQUIRED_KEYWORDS)
                        
                        if (href and title and len(title) > 3 and has_keywords and 
                            ('.pdf' in href.lower() or '/download' in href.lower() or '/file' in href.lower())):
                            
                            full_url = urljoin(base_url, href)
                            
                            if not self.is_duplicate(full_url):
                                self.documents.append({
                                    'title': title,
                                    'url': full_url,
                                    'source': 'Welib.org',
                                    'type': 'PDF'
                                })
                                
                                print(f"   Found: {title}")
                                if self.try_download_document(title, full_url):
                                    self.downloaded_count += 1
                
                except Exception as inner_e:
                    continue
        
        except Exception as e:
            pass
    
    def _process_search_results(self, search_url, source_name):
        """Process search results from a given URL"""
        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                if self.downloaded_count >= MAX_DOWNLOADS:
                    return
                
                href = link.get('href')
                title = link.get_text(strip=True)
                
                # Check if link has keywords in title or in the href
                has_keywords_in_title = self.has_required_keywords(title)
                has_keywords_in_url = any(kw in href.lower() for kw in REQUIRED_KEYWORDS)
                
                # Validate document - more flexible matching
                if (title and len(title) > 3 and
                    (has_keywords_in_title or has_keywords_in_url) and
                    not self.is_duplicate(href) and
                    ('.pdf' in href.lower() or 'download' in href.lower() or 'pdf' in title.lower())):
                    
                    # Make absolute URL if relative
                    full_url = urljoin(search_url, href)
                    
                    if not self.is_duplicate(full_url):
                        self.documents.append({
                            'title': title,
                            'url': full_url,
                            'source': source_name,
                            'type': 'PDF'
                        })
                        
                        print(f"   Found: {title}")
                        if self.try_download_document(title, full_url):
                            self.downloaded_count += 1
        
        except Exception as e:
            pass  # Silently continue on error
    
    def scrape_direct_sources(self):
        """Scrape from direct source URLs"""
        print("🌐 Scraping Direct Sources...")
        
        # Add known public PDF sources that commonly have tutorials
        fallback_pdfs = [
            {
                'title': 'PostgreSQL Tutorial - Official Documentation',
                'url': 'https://www.postgresql.org/docs/current/tutorial.html',
                'source': 'PostgreSQL.org'
            },
            {
                'title': 'Python Official Tutorial',
                'url': 'https://docs.python.org/3/tutorial/',
                'source': 'Python.org'
            },
            {
                'title': 'SQL Tutorial - W3Schools',
                'url': 'https://www.w3schools.com/sql/',
                'source': 'W3Schools'
            },
            {
                'title': 'Python for Data Analysis - Free Online',
                'url': 'https://wesmckinney.com/book/',
                'source': 'O\'Reilly'
            },
            {
                'title': 'Learn SQL - Free Interactive Tutorial',
                'url': 'https://sqlzoo.net/',
                'source': 'SQLZoo'
            },
            {
                'title': 'PostgreSQL Tutorial - TutorialsPoint',
                'url': 'https://www.tutorialspoint.com/postgresql/',
                'source': 'TutorialsPoint'
            },
            {
                'title': 'Python Programming Handbook',
                'url': 'https://handbook.python.org/',
                'source': 'Python'
            },
            {
                'title': 'Database Design Tutorial',
                'url': 'https://www.tutorialspoint.com/database_concepts/',
                'source': 'TutorialsPoint'
            }
        ]
        
        # Add fallback resources
        for pdf in fallback_pdfs:
            if self.downloaded_count >= MAX_DOWNLOADS:
                return
            
            if not self.is_duplicate(pdf['url']):
                self.documents.append(pdf)
                print(f"   Found: {pdf['title']}")
                # Attempt download but don't fail if it's not a direct PDF
                self.try_download_document(pdf['title'], pdf['url'])
        
        # Try scraping configured sources
        for source in DIRECT_SOURCES:
            if not source['enabled'] or self.downloaded_count >= MAX_DOWNLOADS:
                continue
            
            try:
                print(f"   Checking {source['name']}...")
                response = self.session.get(source['url'], timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        if self.downloaded_count >= MAX_DOWNLOADS:
                            return
                        
                        href = link.get('href')
                        title = link.get_text(strip=True)
                        
                        # More flexible matching - look for PDFs with or without keywords
                        is_pdf_link = '.pdf' in href.lower()
                        has_keywords = any(kw in title.lower() or kw in href.lower() for kw in REQUIRED_KEYWORDS)
                        has_any_db_term = any(term in title.lower() or term in href.lower() 
                                             for term in ['sql', 'python', 'postgres', 'database', 'data', 'programming'])
                        
                        if (href and title and len(title) > 2):
                            # Direct PDF links with keywords (highest priority)
                            if is_pdf_link and has_keywords:
                                full_url = urljoin(source['url'], href)
                                if not self.is_duplicate(full_url):
                                    self.documents.append({
                                        'title': title,
                                        'url': full_url,
                                        'source': source['name'],
                                        'type': 'PDF'
                                    })
                                    print(f"   Found PDF: {title}")
                                    if self.try_download_document(title, full_url):
                                        self.downloaded_count += 1
                            
                            # Links that look like book/resource links with keywords
                            elif (('download' in href.lower() or 'pdf' in title.lower() or 
                                   'book' in title.lower() or 'guide' in title.lower()) and 
                                  has_any_db_term):
                                full_url = urljoin(source['url'], href)
                                if not self.is_duplicate(full_url):
                                    print(f"   Found Resource: {title}")
                                    self.documents.append({
                                        'title': title,
                                        'url': full_url,
                                        'source': source['name'],
                                        'type': 'PDF'
                                    })
                                    if self.try_download_document(title, full_url):
                                        self.downloaded_count += 1
            
            except Exception as e:
                pass  # Silently continue on error
    
    # ==================== REPORTING METHODS ====================
    
    def save_documents_list(self):
        """Save list of documents to file"""
        output_file = os.path.join(TARGET_DIR, "downloaded_documents_list.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SQL, Python, and PostgreSQL Documents - Downloaded\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Downloaded: {self.downloaded_count}/{MAX_DOWNLOADS}\n\n")
            
            for idx, doc in enumerate(self.documents[:self.downloaded_count], 1):
                f.write(f"{idx}. {doc['title']}\n")
                f.write(f"   URL: {doc['url']}\n")
                f.write(f"   Source: {doc['source']}\n")
                f.write(f"   Type: {doc['type']}\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"\n✅ Saved documents list to: {output_file}")
    
    def save_config_template(self):
        """Save a template config file for easy updates"""
        config_file = os.path.join(TARGET_DIR, "scraper_config.json")
        
        template = {
            'description': 'Scraper configuration - modify to update URLs and keywords',
            'required_keywords': REQUIRED_KEYWORDS,
            'search_keywords': SEARCH_KEYWORDS,
            'search_sources': SEARCH_SOURCES,
            'direct_sources': DIRECT_SOURCES,
            'max_downloads': MAX_DOWNLOADS
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Saved config template to: {config_file}")
    
    # ==================== MAIN RUN METHOD ====================
    
    def run(self):
        """Execute all scrapers"""
        print("=" * 80)
        print("Starting PDF Document Download Process...")
        print("=" * 80 + "\n")
        
        # Run all scraping methods
        self.scrape_search_sources()
        
        if self.downloaded_count < MAX_DOWNLOADS:
            self.scrape_direct_sources()
        
        # Save results
        self.save_documents_list()
        self.save_config_template()
        
        # Print summary
        print(f"\n{'=' * 80}")
        print(f"✅ Scraping and Download Complete!")
        print(f"📊 Documents Downloaded: {self.downloaded_count}/{MAX_DOWNLOADS}")
        print(f"📁 Location: {TARGET_DIR}")
        print(f"⚙️  Config Template: {os.path.join(TARGET_DIR, 'scraper_config.json')}")
        print(f"{'=' * 80}")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    scraper = PDFScraper()
    scraper.run()
    print("\n✨ Web scraper finished successfully!")