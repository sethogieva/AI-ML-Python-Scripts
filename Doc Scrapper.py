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
REQUIRED_KEYWORDS = ['sql', 'python', 'postgres', 'postgresql']

# Keywords to search for in sources (add or remove keywords here)
SEARCH_KEYWORDS = [
    'SQL', 'Python', 'PostgreSQL',
    'SQL Tutorial', 'Python Tutorial', 'PostgreSQL Tutorial',
    'SQL Beginner', 'Python Beginner', 'PostgreSQL Beginner',
    'SQL Database', 'Python Programming', 'PostgreSQL Database'
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
        'name': 'New PDF Site',
        'base_url': 'https://open.umn.edu/opentextbooks//',
        'search_templates': ['?search={keyword}'],
        'enabled': True
    }
    # ADD MORE SEARCH SOURCES HERE - Example:
    # {
    #     'name': 'New PDF Site',
    #     'base_url': 'https://example.com/',
    #     'search_templates': ['?search={keyword}'],
    #     'enabled': True
    # },
]

# Direct source URLs (pages to scrape for PDF links)
# Just paste URLs here to add new sources!
DIRECT_SOURCES = [
    {
        'name': 'SQL Tutorial - W3Schools',
        'url': 'https://open.umn.edu/opentextbooks/subjects/databases',
        'enabled': True
    },

# ADD MORE DIRECT SOURCES HERE - Example:
    # {
    #     'name': 'Another PDF Source',
    #     'url': 'https://example.com/tutorials/',
    #     'enabled': True
    # },
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
            
            for keyword in SEARCH_KEYWORDS:
                if self.downloaded_count >= MAX_DOWNLOADS:
                    break
                
                for template in source['search_templates']:
                    if self.downloaded_count >= MAX_DOWNLOADS:
                        break
                    
                    search_url = source['base_url'] + template.format(keyword=keyword)
                    self._process_search_results(search_url, source['name'])
    
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
                
                # Validate document
                if (self.is_valid_pdf_url(href) and 
                    title and 
                    len(title) > 3 and
                    self.has_required_keywords(title) and
                    not self.is_duplicate(href)):
                    
                    self.documents.append({
                        'title': title,
                        'url': href,
                        'source': source_name,
                        'type': 'PDF'
                    })
                    
                    print(f"   Found: {title}")
                    if self.try_download_document(title, href):
                        self.downloaded_count += 1
        
        except Exception as e:
            pass  # Silently continue on error
    
    def scrape_direct_sources(self):
        """Scrape from direct source URLs"""
        print("🌐 Scraping Direct Sources...")
        
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
                        
                        if (href and '.pdf' in href.lower() and title and len(title) > 3):
                            full_url = urljoin(source['url'], href)
                            
                            if not self.is_duplicate(full_url):
                                print(f"   Found PDF: {title}")
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