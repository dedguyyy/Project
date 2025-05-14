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
    surahs_map = {s['number']: s for s in surahs_data['data']} if surahs_data else {}
    
    results = []
    for match in search_data['data']['matches']:
        surah_num = match['surah']['number']
        surah_info = surahs_map.get(surah_num, {})
        
        results.append({
            'text': match['text'],
            'translation': match['translation'],
            'surah_number': surah_num,
            'surah_name': surah_info.get('englishName', ''),
            'surah_name_arabic': surah_info.get('name', ''),
            'ayah_number': match['numberInSurah']
        })
    
    pagination = {
        'total': search_data['data']['total'],
        'current_page': int(request.args.get('offset', 0)) // 20 + 1,
        'total_pages': (search_data['data']['total'] + 19) // 20,
        'has_next': search_data['data']['total'] > (int(request.args.get('offset', 0)) + 20),
        'has_prev': int(request.args.get('offset', 0)) > 0
    }
    
    return render_template('search.html',
                         results=results,
                         query=query,
                         pagination=pagination,
                         surahs=surahs_data['data'] if surahs_data else [])

@app.route('/api/surahs')
def get_surahs():
    """API endpoint for surah list"""
    surahs_data = get_quran_data("surah")
    return jsonify(surahs_data['data'] if surahs_data else [])

@app.route('/surah/<int:surah_number>')
def get_surah(surah_number):
    """Endpoint for individual surah"""
    data = get_quran_data(f"surah/{surah_number}/en.sahih")
    if data and data.get('data'):
        return render_template('surah.html', surah=data['data'])
    return render_template('error.html', message="Error fetching Surah data"), 500

@app.route('/bukhari')
def bukhari():
    """Hadith collection - Bukhari"""
    pdf_text = extract_text_from_pdf_url(PDF_URLS['bukhari'])
    if not pdf_text:
        return render_template('error.html', message="Error loading Bukhari content"), 500
    return render_template('bukhari.html', pdf_text=pdf_text)

@app.route('/muslim')
def muslim():
    """Hadith collection - Muslim"""
    pdf_text = extract_text_from_pdf_url(PDF_URLS['muslim'])
    if not pdf_text:
        return render_template('error.html', message="Error loading Muslim content"), 500
    return render_template('muslim.html', pdf_text=pdf_text)

@app.route('/tirmidhi')
def tirmidhi():
    """Hadith collection - Tirmidhi"""
    pdf_text = extract_text_from_pdf_url(PDF_URLS['tirmidhi'])
    if not pdf_text:
        return render_template('error.html', message="Error loading Tirmidhi content"), 500
    return render_template('tirmidhi.html', pdf_text=pdf_text)

@app.route('/generic')
def generic():
    """Generic page template"""
    return render_template('generic.html')

@app.route('/elements')
def elements():
    """Elements page template"""
    return render_template('elements.html')

# Error handler
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {str(error)}")
    return render_template('error.html', message="Internal server error"), 500

# Note: The __name__ == '__main__' block is not needed for Vercel deployment