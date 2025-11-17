# Quick Reference - Adding New Scrape URLs

## 📍 Where to Find URLs in Doc Scrapper.py

### Option 1: Search Sources (for sites with search functionality)
**Location**: Lines 30-50

**Current Example:**
```python
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
    # 👈 PASTE NEW SOURCES HERE
]
```

**To Add a New Search Source:**
Copy this template and replace values:
```python
    {
        'name': 'Your Site Name Here',
        'base_url': 'https://example.com/',
        'search_templates': ['?search={keyword}', '/find?q={keyword}'],
        'enabled': True
    },
```

**Instructions:**
1. Change `'name'` to your site's name
2. Change `'base_url'` to the root URL
3. Change `'search_templates'` to match the site's search URL patterns
4. Keep `'enabled': True` (or `False` to disable)

---

### Option 2: Direct Sources (for pages with PDF links)
**Location**: Lines 54-73

**Current Example:**
```python
DIRECT_SOURCES = [
    {
        'name': 'SQL Tutorial - W3Schools',
        'url': 'https://www.w3schools.com/sql/',
        'enabled': True
    },
    {
        'name': 'Python Tutorial - Python.org',
        'url': 'https://www.python.org/downloads/',
        'enabled': True
    },
    {
        'name': 'PostgreSQL Documentation',
        'url': 'https://www.postgresql.org/docs/current/',
        'enabled': True
    },
    # 👈 PASTE NEW SOURCES HERE
]
```

**To Add a New Direct Source:**
Copy this template and replace values:
```python
    {
        'name': 'Your Source Name Here',
        'url': 'https://example.com/documents/',
        'enabled': True
    },
```

**Instructions:**
1. Change `'name'` to your source's name
2. Change `'url'` to the page URL
3. Keep `'enabled': True` (or `False` to disable)

---

## 📝 Real Examples

### Example 1: Adding LibGen (Search Source)
```python
    {
        'name': 'LibGen Library',
        'base_url': 'https://libgen.is/',
        'search_templates': ['?req={keyword}'],
        'enabled': True
    },
```

### Example 2: Adding GitHub (Direct Source)
```python
    {
        'name': 'GitHub Documentation',
        'url': 'https://github.com/search?q=sql+python+tutorial',
        'enabled': True
    },
```

### Example 3: Adding O'Reilly Books (Search Source)
```python
    {
        'name': 'OReilly Books',
        'base_url': 'https://www.oreilly.com/',
        'search_templates': ['/search/?q={keyword}'],
        'enabled': True
    },
```

---

## 🔍 Finding Search URL Pattern

**To find the search template for a website:**

1. Go to the website
2. Search for something (e.g., "SQL")
3. Look at the URL in address bar
4. Identify the search parameter

**Examples:**
- `https://site.com/?s=SQL` → `'?s={keyword}'`
- `https://site.com/search?q=SQL` → `'/search?q={keyword}'`
- `https://site.com/books/find/SQL` → `'/books/find/{keyword}'`
- `https://site.com:8080/search?term=SQL` → `'/search?term={keyword}'`

---

## ⚡ Quick Steps

1. **Open** `Doc Scrapper.py`
2. **Go to** line 30-50 (search) or 54-73 (direct)
3. **Find** the comment that says `# ADD MORE HERE`
4. **Copy** the template above the comment
5. **Paste** it before the closing bracket `]`
6. **Replace** the values with your URL
7. **Save** the file
8. **Run** `python "Doc Scrapper.py"`

---

## 💡 Tips

- **Commas Matter**: Each entry needs a comma after the closing `}`
- **Last Entry**: The last entry should NOT have a comma before the `]`
- **Enabled Flag**: Set to `False` to skip a source without deleting
- **Search Templates**: Can have multiple patterns per site

---

## 📞 Format Reference

### Search Source Format
```python
{
    'name': str,                           # Display name
    'base_url': str,                       # Root URL
    'search_templates': [str, str, ...],   # URL patterns with {keyword}
    'enabled': bool                        # True or False
}
```

### Direct Source Format
```python
{
    'name': str,      # Display name
    'url': str,       # Full page URL
    'enabled': bool   # True or False
}
```

---

**That's it! Just paste and go!** 🚀
