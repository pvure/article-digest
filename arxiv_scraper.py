import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime
import time
from tqdm import tqdm

class ArXivDigest:
    def __init__(self, category="q-bio.BM"):
        self.category = category
        self.base_url = f"https://arxiv.org/list/{category}/recent"
        self.output_dir = 'arxiv_digests'
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_papers(self):
        """Scrape recent papers from arXiv"""
        print("Scraping papers from arXiv...")
        
        # Make the request to arXiv
        r = requests.get(self.base_url)
        if r.status_code != 200:
            print(f"Failed to retrieve data: Status code {r.status_code}")
            return None
        
        # Parse the HTML
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Initialize lists to store data
        dates = []
        titles = []
        authors_list = []
        article_ids = []
        abstracts = []
        
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
                            
                            # Extract title
                            title_div = dd.find('div', {'class': 'list-title'})
                            if title_div:
                                title = title_div.text.replace('Title:', '').strip()
                                titles.append(title)
                            else:
                                titles.append('')
                            
                            # Extract authors
                            authors_div = dd.find('div', {'class': 'list-authors'})
                            if authors_div:
                                author_links = authors_div.find_all('a')
                                authors = [author.text.strip() for author in author_links]
                                authors_list.append(', '.join(authors))
                            else:
                                authors_list.append('')
                            
                            # Add date
                            dates.append(current_date)
                            
                            # Get abstract (will be fetched separately)
                            abstracts.append("")
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Title': titles,
            'Authors': authors_list,
            'Article ID': article_ids,
            'Abstract': abstracts
        })
        
        return df
    
    def fetch_abstracts(self, df):
        """Fetch abstracts for papers in DataFrame"""
        print("Fetching abstracts...")
        
        for i, row in tqdm(df.iterrows(), total=len(df)):
            paper_id = row['Article ID'].split(':')[1] if ':' in row['Article ID'] else row['Article ID']
            abstract_url = f"https://arxiv.org/abs/{paper_id}"
            
            try:
                # Add delay to be respectful to the server
                time.sleep(1)
                
                abstract_response = requests.get(abstract_url)
                if abstract_response.status_code != 200:
                    print(f"Failed to get abstract page for {paper_id}")
                    continue
                
                # Parse abstract page
                abstract_soup = BeautifulSoup(abstract_response.content, 'html.parser')
                abstract_div = abstract_soup.find('blockquote', {'class': 'abstract'})
                
                if abstract_div:
                    abstract_text = abstract_div.text.strip()
                    # Remove "Abstract: " prefix if present
                    abstract_text = abstract_text.replace('Abstract:', '').strip()
                    df.at[i, 'Abstract'] = abstract_text
                else:
                    print(f"Could not find abstract for {paper_id}")
            
            except Exception as e:
                print(f"Error getting abstract for {paper_id}: {str(e)}")
        
        return df
    
    def save_data(self, df):
        """Save the DataFrame to CSV"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        df_path = os.path.join(self.output_dir, f'papers_{date_str}.csv')
        df.to_csv(df_path, index=False)
        print(f"Paper data saved to {df_path}")
    
    def create_combined_abstracts_file(self, df):
        """Create a combined file with all abstracts"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        combined_file_path = os.path.join(self.output_dir, f'all_abstracts_{date_str}.md')
        
        with open(combined_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# arXiv {self.category} Papers - {date_str}\n\n")
            
            for i, row in df.iterrows():
                f.write(f"## Paper {i+1}: {row['Title']}\n\n")
                f.write(f"**Authors:** {row['Authors']}\n\n")
                f.write(f"**Date:** {row['Date']}\n\n")
                f.write(f"**ID:** {row['Article ID']}\n\n")
                f.write("**Abstract:**\n\n")
                f.write(f"{row['Abstract']}\n\n")
                f.write("---\n\n")
        
        print(f"Combined abstracts file created at {combined_file_path}")
    
    def run(self):
        """Run the complete digest workflow"""
        print("Starting arXiv digest workflow...")
        
        # Scrape papers
        df = self.scrape_papers()
        if df is None or len(df) == 0:
            print("No papers found. Exiting.")
            return None, None
        
        print(f"Found {len(df)} papers")
        
        # Fetch abstracts
        df = self.fetch_abstracts(df)
        
        # Save data to CSV
        self.save_data(df)
        
        # Create combined abstracts file
        self.create_combined_abstracts_file(df)
        
        print("Digest workflow completed successfully")
        return df


# Main application for command line usage
def main():
    # Create ArXiv digest
    arxiv_digest = ArXivDigest(category="q-bio.BM")
    
    # Run the digest workflow
    df = arxiv_digest.run()

if __name__ == "__main__":
    main()