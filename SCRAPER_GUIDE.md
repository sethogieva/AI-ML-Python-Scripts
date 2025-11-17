# PDF Scraper - Configuration Guide

## Overview
This scraper downloads PDF documents related to SQL, Python, and PostgreSQL from multiple sources.

## Quick Start

### Running the Scraper
```bash
python "Doc Scrapper.py"
```

## Configuration - Lines 1-75

All configuration is at the TOP of the file for easy access and editing.

### 1. Basic Settings (Lines 10-13)
```python
TARGET_DIR = r"C:\Users\user\Desktop\Python Course\SQL, Pyth, and PostGres Docs"
MAX_DOWNLOADS = 20
REQUIRED_KEYWORDS = ['sql', 'python', 'postgres', 'postgresql']
```
- **TARGET_DIR**: Where PDFs will be saved
- **MAX_DOWNLOADS**: How many PDFs to download (0-unlimited)
- **REQUIRED_KEYWORDS**: PDFs must contain at least one of these keywords

### 2. Search Keywords (Lines 19-25)
```python
SEARCH_KEYWORDS = [
    'SQL', 'Python', 'PostgreSQL',
    'SQL Tutorial', 'Python Tutorial', 'PostgreSQL Tutorial',
    'SQL Beginner', 'Python Beginner', 'PostgreSQL Beginner',
    'SQL Database', 'Python Programming', 'PostgreSQL Database'
]
```
**To Change**: Simply add or remove keywords from this list.

### 3. Search Sources (Lines 30-50)
These are websites with search functionality that the scraper will query.

**To Add a New Search Source**, add this template:
```python
{
    'name': 'Your Site Name',
    'base_url': 'https://example.com/',
    'search_templates': ['?s={keyword}', '/search?q={keyword}'],
    'enabled': True
},
```
- **name**: Display name for the source
- **base_url**: Root URL of the site
- **search_templates**: URL patterns (replace search term with `{keyword}`)
- **enabled**: Set to `False` to disable a source

### 4. Direct Sources (Lines 54-73)
These are pages where the scraper looks for PDF links directly.

**To Add a New Direct Source**, add this template:
```python
{
    'name': 'Your Source Name',
    'url': 'https://example.com/documents/',
    'enabled': True
},
```

## Output Files

After running, you'll get:

1. **downloaded_documents_list.txt** - List of downloaded PDFs
2. **scraper_config.json** - Backup of your configuration
3. **PDF files** - All downloaded documents

## Examples

### Example 1: Add a New PDF Site
To add "LibGen.is" as a source:

```python
SEARCH_SOURCES = [
    # ... existing sources ...
    {
        'name': 'LibGen',
        'base_url': 'https://libgen.is/',
        'search_templates': ['?req={keyword}'],
        'enabled': True
    },
]
```

### Example 2: Change Search Keywords
To search only for SQL and PostgreSQL:

```python
REQUIRED_KEYWORDS = ['sql', 'postgres', 'postgresql']

SEARCH_KEYWORDS = [
    'SQL', 'PostgreSQL',
    'SQL Tutorial', 'PostgreSQL Tutorial',
    'SQL Beginner', 'PostgreSQL Beginner',
]
```

### Example 3: Download More Documents
```python
MAX_DOWNLOADS = 50  # Instead of 20
```

### Example 4: Disable a Source
Set `'enabled': False`:

```python
{
    'name': 'PDFDrive (webs.nf)',
    'base_url': 'https://pdfdrive.webs.nf/',
    'search_templates': ['?s={keyword}', '/search?q={keyword}'],
    'enabled': False  # <-- Changed to False
},
```

## How It Works

1. **Searches** - Uses SEARCH_SOURCES to search for documents
2. **Filters** - Only keeps PDFs with required keywords in title
3. **Downloads** - Downloads matching PDFs to TARGET_DIR
4. **Validates** - Checks for duplicates and existing files
5. **Reports** - Creates a list of downloaded documents

## Tips

- **URL Patterns**: The `{keyword}` in search_templates gets replaced with each search term
  - Example: `'?s={keyword}'` becomes `'?s=SQL'`, `'?s=Python'`, etc.

- **Enable/Disable**: Quickly disable sources by setting `'enabled': False` instead of deleting

- **Order Matters**: Sources are processed in order. Put high-quality sources first

- **Keywords**: More specific keywords = fewer results, but more relevant

## Troubleshooting

**No PDFs Found?**
- Check if target websites are working
- Try adding different SEARCH_KEYWORDS
- Add more SEARCH_SOURCES

**Want More PDFs?**
- Increase MAX_DOWNLOADS
- Add more keywords to SEARCH_KEYWORDS
- Add more sources to SEARCH_SOURCES

**Only Get a Few PDFs?**
- Some sites may block scraping
- Try adding alternative sources
- Adjust keyword combinations
