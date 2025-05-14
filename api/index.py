from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import PyPDF2
from io import BytesIO
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Required for Vercel deployment
api = app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# External PDF URLs (replace these with your actual PDF URLs)
PDF_URLS = {
    'bukhari': 'https://example.com/path/to/bukhari.pdf',
    'muslim': 'https://example.com/path/to/muslim.pdf',
    'tirmidhi': 'https://example.com/path/to/tirmidhi.pdf'
}

def extract_text_from_pdf_url(pdf_url):
    """Extract text from PDF using URL instead of local file"""
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        with BytesIO(response.content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        logger.error(f"Error reading PDF from {pdf_url}: {str(e)}")
        return None

def get_quran_data(endpoint, params=None):
    """Helper function to fetch Quran API data"""
    base_url = "https://api.alquran.cloud/v1/"
    try:
        response = requests.get(base_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API Error ({endpoint}): {str(e)}")
        return None

@app.route('/')
def home():
    """Homepage showing list of surahs"""
    data = get_quran_data("surah")
    if data and data.get('data'):
        return render_template('index.html', surahs=data['data'])
    return render_template('error.html', message="Error fetching Surah list"), 500

@app.route('/search')
def search_quran():
    """Search endpoint for Quran verses"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', error="Please enter a search term")
    
    search_params = {
        'q': query,
        'language': 'en',
        'surah': request.args.get('surah', ''),
        'offset': request.args.get('offset', 0),
        'limit': 20
    }
    
    search_data = get_quran_data("search", params=search_params)
    
    if not search_data or not search_data.get('data'):
        return render_template('search.html', 
                           error="No results found",
                           query=query)
    
    surahs_data = get_quran_data("surah")
    surahs_map = {s['number']: s for s in surahs_data['data']} if surahs