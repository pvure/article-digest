import os
import re
from google import genai
from tqdm import tqdm
import time
import markdown2
from bs4 import BeautifulSoup

def read_markdown_file(file_path):
    """Read and parse markdown file into sections"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by papers (each paper section starts with "## Paper")
    paper_sections = re.split(r'## Paper \d+:', content)[1:]  # Skip the first element which is the header
    
    # Extract titles from the main content to pair with sections
    titles = re.findall(r'## Paper \d+: (.*?)\n', content)
    
    paper_data = []
    for i, section in enumerate(paper_sections):
        if i < len(titles):
            paper_data.append({
                'title': titles[i],
                'content': section.strip()
            })
    
    return paper_data

def summarize_with_gemini(api_key, paper_data):
    """Summarize paper abstracts using Gemini API"""
    client = genai.Client(api_key=api_key)
    
    summaries = []
    
    for paper in tqdm(paper_data, desc="Summarizing abstracts"):
        # Extract the abstract portion from the paper content
        abstract_match = re.search(r'\*\*Abstract:\*\*\n\n(.*?)(?:\n\n---|\Z)', paper['content'], re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
        else:
            abstract = "Abstract not found"
        
        # Create prompt for Gemini
        prompt = f"""Summarize the following scientific abstract in 2-3 sentences. 
Also include one sentence on why this research is important to the field.

Paper Title: {paper['title']}
Abstract: {abstract}

Format your response as:
- Summary: [2-3 sentence summary]
- Significance: [1 sentence on importance]
"""
        
        try:
            # Add a small delay to avoid rate limits
            time.sleep(0.5)
            
            # Call Gemini API
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite", 
                contents=prompt
            )
            
            summary = response.text.strip()
            
            # Store the summary with the paper title
            summaries.append({
                'title': paper['title'],
                'original_content': paper['content'],
                'summary': summary
            })
            
        except Exception as e:
            print(f"Error summarizing '{paper['title']}': {str(e)}")
            summaries.append({
                'title': paper['title'],
                'original_content': paper['content'],
                'summary': f"Error generating summary: {str(e)}"
            })
    
    return summaries

def create_summary_file(summaries, output_path):
    """Create a formatted file with all summaries"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# arXiv Paper Summaries - {time.strftime('%Y-%m-%d')}\n\n")
        
        for i, paper in enumerate(summaries):
            f.write(f"## {i+1}. {paper['title']}\n\n")
            f.write(f"{paper['summary']}\n\n")
            f.write("---\n\n")
    
    print(f"Summary file created at {output_path}")

def main():
    # Configuration
    api_key = "key"  # Replace with your actual Gemini API key
    
    # Find the most recent abstracts file
    abstracts_dir = "arxiv_digests"
    abstracts_files = [f for f in os.listdir(abstracts_dir) if f.startswith("all_abstracts_") and f.endswith(".md")]
    
    if not abstracts_files:
        print("No abstracts files found. Run the scraper first.")
        return
    
    # Get the most recent file
    latest_file = sorted(abstracts_files)[-1]
    abstracts_file_path = os.path.join(abstracts_dir, latest_file)
    
    print(f"Processing file: {abstracts_file_path}")
    
    # Read and parse the markdown file
    paper_data = read_markdown_file(abstracts_file_path)
    print(f"Found {len(paper_data)} papers")
    
    # Summarize abstracts
    summaries = summarize_with_gemini(api_key, paper_data)
    
    # Create output file
    date_str = time.strftime('%Y-%m-%d')
    output_path = os.path.join(abstracts_dir, f"summaries_{date_str}.md")
    create_summary_file(summaries, output_path)

if __name__ == "__main__":
    main()