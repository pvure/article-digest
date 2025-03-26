import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Making a GET request
r = requests.get('https://arxiv.org/list/q-bio.BM/recent')

# Check status code
if r.status_code != 200:
    print(f"Failed to retrieve data: Status code {r.status_code}")
    exit()

# Parsing the HTML
soup = BeautifulSoup(r.content, 'html.parser')

# Initialize lists to store data
dates = []
titles = []
authors_list = []
pdf_links = []
article_ids = []

# Find all dl elements with id="articles"
dl_elements = soup.find_all('dl', id='articles')

for dl in dl_elements:
    # Get the date from the preceding h3 element
    date_header = dl.find_previous('h3')
    if date_header:
        date_text = date_header.text.strip()
        # Extract just the date part
        date_match = re.search(r'[A-Za-z]+, \d+ [A-Za-z]+ \d+', date_text)
        if date_match:
            current_date = date_match.group(0)
            
            # Get all dt (definition term) elements in this dl
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')
            
            for dt, dd in zip(dt_elements, dd_elements):
                # Extract article ID
                id_link = dt.find('a', {'title': 'Abstract'})
                if id_link:
                    article_id = id_link.text.strip()
                    article_ids.append(article_id)
                    
                    # Extract PDF link
                    pdf_link = dt.find('a', {'title': 'Download PDF'})
                    if pdf_link:
                        pdf_links.append('https://arxiv.org' + pdf_link['href'])
                    else:
                        pdf_links.append('')
                    
                    # Extract title
                    title_div = dd.find('div', {'class': 'list-title'})
                    if title_div:
                        # Remove the "Title:" text
                        title = title_div.text.replace('Title:', '').strip()
                        titles.append(title)
                    else:
                        titles.append('')
                    
                    # Extract authors
                    authors_div = dd.find('div', {'class': 'list-authors'})
                    if authors_div:
                        # Get all author links
                        author_links = authors_div.find_all('a')
                        authors = [author.text.strip() for author in author_links]
                        authors_list.append(', '.join(authors))
                    else:
                        authors_list.append('')
                    
                    # Add date
                    dates.append(current_date)

# Create DataFrame
df = pd.DataFrame({
    'Date': dates,
    'Title': titles,
    'Authors': authors_list,
    'PDF Link': pdf_links,
    'Article ID': article_ids
})

# Display the DataFrame
print(df.head())

# Save to CSV if needed
df.to_csv('arxiv_recent_papers.csv', index=False)