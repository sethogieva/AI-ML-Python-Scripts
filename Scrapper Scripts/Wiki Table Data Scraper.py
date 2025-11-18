import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://en.wikipedia.org/wiki/Cloud-computing_comparison'

# Add a fake browser header (important!)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

# Find ALL tables on the page
tables = soup.find_all('table')

print(f"Found {len(tables)} tables")

dfs = []   # list to store DataFrames

# Loop through every table found
for i, table in enumerate(tables):

    # Get table name (from caption if it exists, otherwise use generic name)
    table_name = f"table_{i}"
    caption = table.find('caption')
    if caption:
        table_name = caption.text.strip()
        # Clean up filename (remove special characters)
        table_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in table_name)
        table_name = table_name.replace(' ', '_')

    # Get headers (if they exist)
    table_headers = []
    header_row = table.find('tr')
    if header_row:
        th_tags = header_row.find_all('th')
        if th_tags:
            table_headers = [th.text.strip() for th in th_tags]

    # Extract rows
    rows = table.find_all('tr')[1:]  # skip header row
    data = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        cols = [col.text.strip() for col in cols]
        if any(cols):  # skip empty rows
            data.append(cols)

    # Convert to DataFrame
    if data:
        # Find the maximum number of columns in the data
        max_cols = max(len(row) for row in data) if data else 0
        
        # Pad headers if needed or trim if we have too many
        if table_headers:
            if len(table_headers) < max_cols:
                # Add generic column names for extra columns
                table_headers = table_headers + [f"Column_{i}" for i in range(len(table_headers), max_cols)]
            else:
                # Trim headers to match data
                table_headers = table_headers[:max_cols]
            df = pd.DataFrame(data, columns=table_headers)
        else:
            df = pd.DataFrame(data)
    else:
        df = pd.DataFrame()

    dfs.append(df)

    # Save each table separately with meaningful name
    df.to_csv(f'{table_name}.csv', index=False)
    print(f"Saved {table_name}.csv")

print("Done scraping all tables!")

