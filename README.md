# arXiv Paper Digest Tool

This tool helps you collect and summarize recent scientific papers from arXiv ([ from this specific page](https://arxiv.org/list/q-bio.BM/new)). It saves you time by automatically gathering papers, fetching their abstracts, and creating AI-generated summaries.

## What This Tool Does

1. **Collects Papers**: Gathers recent papers from arXiv in the biomolecular field
2. **Fetches Abstracts**: Gets the full abstract for each paper
3. **Creates Summaries**: Uses Google's Gemini AI to create concise summaries

## Requirements Before Starting

- A computer with Python installed (version 3.7 or newer)
- An internet connection
- A Google API key for using Gemini (see "Setting Up" section)

## Setting Up

### 1. Download This Repository

- Click the green "Code" button at the top of this GitHub page
- Select "Download ZIP"
- Unzip the file to a folder on your computer

### 2. Install Required Packages

Open your command prompt or terminal and navigate to the folder where you unzipped the files. Then run:

```
pip install requests beautifulsoup4 pandas tqdm google-generativeai markdown2
```

### 3. Get a Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Log in with your Google account
3. Click "Create API Key"
4. Copy your new API key

### 4. Set Up Your API Key

Open the file `gemini_summarizer.py` in a text editor and replace:

```python
api_key = "key"  # Replace with your actual Gemini API key
```

with your actual API key:

```python
api_key = "YOUR_API_KEY_HERE"  # Replace with your actual Gemini API key
```

Also update the API key in `gemini_api.py` with your key.

## Using the Tool

### Step 1: Collect Papers and Abstracts

Open your command prompt or terminal, navigate to the folder with the files, and run:

```
python arxiv_scraper.py
```

This will:
- Download recent biomolecular papers from arXiv
- Fetch their abstracts
- Save everything to a CSV file and a markdown file in the `arxiv_digests` folder

### Step 2: Generate Summaries

After running the scraper, run:

```
python gemini_summarizer.py
```

This will:
- Process the abstracts collected in Step 1
- Create AI-generated summaries for each paper
- Save the summaries to a markdown file in the `arxiv_digests` folder

## Viewing the Results

After running both scripts, you can find these files in the `arxiv_digests` folder:

1. `papers_YYYY-MM-DD.csv` - A spreadsheet with all paper details
2. `all_abstracts_YYYY-MM-DD.md` - A text file with all paper details and abstracts
3. `summaries_YYYY-MM-DD.md` - A text file with AI-generated summaries

To view the summary file, you can:
- Open it in any text editor
- Use a markdown viewer for better formatting
- Copy and paste the content into a markdown viewer online

## Customizing

By default, this tool collects papers from the "q-bio.BM" (Biomolecular) category. If you want to change the category:

1. Open `arxiv_scraper.py` in a text editor
2. Find the line: `arxiv_digest = ArXivDigest(category="q-bio.BM")`
3. Change "q-bio.BM" to another arXiv category code

## Troubleshooting

**Problem**: Error about missing packages
**Solution**: Make sure you've installed all required packages with the pip command above

**Problem**: "API key not valid" error
**Solution**: Double-check that you've correctly copied your Google API key into both Python files

**Problem**: No papers found
**Solution**: Make sure your internet connection is working and try again

## Need Help?

If you encounter any issues, please:
1. Check the error message for clues
2. Make sure all setup steps were completed correctly
3. Create an issue on this GitHub repository