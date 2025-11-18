# ⚡ Quick Reference Card

## 🎯 Where Everything Is

```
Doc Scrapper.py
├─ Line 10  → TARGET_DIR          (Where to save PDFs)
├─ Line 13  → MAX_DOWNLOADS       (How many to get)
├─ Line 16  → REQUIRED_KEYWORDS   (PDF must contain)
├─ Line 19  → SEARCH_KEYWORDS     (What to search)
├─ Line 30  → SEARCH_SOURCES      ⭐ ADD URLS HERE
├─ Line 54  → DIRECT_SOURCES      ⭐ ADD URLS HERE
└─ Line 322 → RUN SCRAPER         (Execute)
```

## 🔧 Most Common Changes

### Change Target Directory
**Line 10:**
```python
TARGET_DIR = r"C:\New\Path\Here"
```

### Change Number of Downloads
**Line 13:**
```python
MAX_DOWNLOADS = 50  # Instead of 20
```

### Add Search Keywords
**Lines 19-25:**
```python
SEARCH_KEYWORDS = [
    'SQL', 'Python', 'PostgreSQL',
    'Your Keyword Here',  # ← ADD HERE
]
```

### Add Search Source URL
**Lines 30-50:**
```python
SEARCH_SOURCES = [
    # ... existing sources ...
    {                                    # ← COPY THIS
        'name': 'Your Site Name',        # ← EDIT THIS
        'base_url': 'https://site.com/', # ← EDIT THIS
        'search_templates': ['?s={keyword}'],  # ← EDIT THIS
        'enabled': True
    },                                   # ← TO HERE
]
```

### Add Direct Source URL
**Lines 54-73:**
```python
DIRECT_SOURCES = [
    # ... existing sources ...
    {                                    # ← COPY THIS
        'name': 'Your Source Name',      # ← EDIT THIS
        'url': 'https://example.com/',   # ← EDIT THIS
        'enabled': True
    },                                   # ← TO HERE
]
```

### Disable a Source
**Find the source, change:**
```python
'enabled': True   # Change this to False
```

## 📋 Copy-Paste Templates

### Template 1: Search Source
```python
    {
        'name': 'SITE NAME HERE',
        'base_url': 'https://example.com/',
        'search_templates': ['?s={keyword}'],
        'enabled': True
    },
```

### Template 2: Direct Source
```python
    {
        'name': 'SOURCE NAME HERE',
        'url': 'https://example.com/docs/',
        'enabled': True
    },
```

## 🚀 Run It
```bash
python "Doc Scrapper.py"
```

## 📊 Output Location
```
C:\Users\user\Desktop\Python Course\SQL, Pyth, and PostGres Docs\
├── *.pdf                        (Downloaded files)
├── downloaded_documents_list.txt (List of files)
└── scraper_config.json          (Config backup)
```

## ✅ Before You Run

- [ ] Added any new URLs? Check QUICK_URL_GUIDE.md
- [ ] Updated keywords? Check line 16-25
- [ ] Set correct save path? Check line 10
- [ ] Have beautifulsoup4 & requests? `pip install beautifulsoup4 requests`

## 🎓 Learn More

| File | Contains |
|------|----------|
| README.md | Complete overview |
| QUICK_URL_GUIDE.md | How to add URLs (with examples) |
| SCRAPER_GUIDE.md | Detailed configuration |
| STRUCTURE_DIAGRAM.md | Code structure visualization |
| REFACTORING_SUMMARY.md | What changed & why |

## 💾 Configuration Quick Edit

**Most editing happens in Lines 7-75 of Doc Scrapper.py:**

```python
# Lines 10-13: Basic Settings
TARGET_DIR = ...
MAX_DOWNLOADS = ...

# Lines 16: What PDFs must contain
REQUIRED_KEYWORDS = [...]

# Lines 19-25: What to search for
SEARCH_KEYWORDS = [...]

# Lines 30-50: Search sites (paste URLs here)
SEARCH_SOURCES = [
    { ... },
    { ... },
    # ← PASTE NEW URLS HERE
]

# Lines 54-73: Pages with PDFs (paste URLs here)
DIRECT_SOURCES = [
    { ... },
    { ... },
    # ← PASTE NEW URLS HERE
]
```

---

**That's it! The code handles the rest.** 🎉
