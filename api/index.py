from flask import Flask, render_template, request, jsonify
import requests
import PyPDF2
from io import BytesIO
import logging
import traceback

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Required for Vercel deployment
api = app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# External resource URLs (replace with your actual URLs)
RESOURCE_URLS = {
    'bukhari': 'https://your-cdn-url/bukhari.pdf',
    'muslim': 'https://your-cdn-url/muslim.pdf',
    'tirmidhi': 'https://your-cdn-url/tirmidhi.pdf',
    'quran_api': 'https://api.alquran.cloud/v1/'
}

def safe_pdf_extraction(pdf_url):
    """Safely extract text from PDF with comprehensive error handling"""
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        
        with BytesIO(response.content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "\n".join(
                page.extract_text() 
                for page in reader.pages 
                if page.extract_text()
            )
            return text
    except Exception as e:
        logger.error(f"PDF Extraction Failed: {str(e)}\n{traceback.format_exc()}")
        return None

def fetch_quran_data(endpoint, params=None):
    """Robust API data fetcher with timeout and error handling"""
    try:
        response = requests.get(
            RESOURCE_URLS['quran_api'] + endpoint,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Quran API Error: {str(e)}\n{traceback.format_exc()}")
        return None

@app.route('/')
def home():
    """Homepage with surah list"""
    try:
        data = fetch_quran_data("surah")
        if data and data.get('data'):
            return render_template('index.html', surahs=data['data'])
        return render_template('error.html', message="Failed to load surah list"), 500
    except Exception as e:
        logger.error(f"Homepage Error: {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html', message="Server error"), 500

@app.route('/search')
def search_quran():
    """Search endpoint with pagination"""
    try:
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
        
        search_data = fetch_quran_data("search", params=search_params)
        if not search_data or not search_data.get('data'):
            return render_template('search.html', error="No results found", query=query)

        surahs_data = fetch_quran_data("surah")
        surahs_map = {s['number']: s for s in surahs_data['data']} if surahs_data else {}

        results = [{
            'text': match['text'],
            'translation': match['translation'],
            'surah_number': match['surah']['number'],
            'surah_name': surahs_map.get(match['surah']['number'], {}).get('englishName', ''),
            'surah_name_arabic': surahs_map.get(match['surah']['number'], {}).get('name', ''),
            'ayah_number': match['numberInSurah']
        } for match in search_data['data']['matches']]

        pagination = {
            'total': search_data['data']['total'],
            'current_page': int(request.args.get('offset', 0)) // 20 + 1,
            'total_pages': (search_data['data']['total'] + 19) // 20,
            'has_next': search_data['data']['total'] > (int(request.args.get('offset', 0)) + 20),
            'has_prev': int(request.args.get('offset', 0)) > 0
        }

        return render_template(
            'search.html',
            results=results,
            query=query,
            pagination=pagination,
            surahs=surahs_data['data'] if surahs_data else []
        )
    except Exception as e:
        logger.error(f"Search Error: {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html', message="Search failed"), 500

@app.route('/surah/<int:surah_number>')
def surah_detail(surah_number):
    """Surah detail page"""
    try:
        data = fetch_quran_data(f"surah/{surah_number}/en.sahih")
        if data and data.get('data'):
            return render_template('surah.html', surah=data['data'])
        return render_template('error.html', message="Surah not found"), 404
    except Exception as e:
        logger.error(f"Surah Detail Error: {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html', message="Failed to load surah"), 500

@app.route('/hadith/<collection>')
def hadith_collection(collection):
    """Generic hadith collection handler"""
    try:
        if collection not in RESOURCE_URLS:
            return render_template('error.html', message="Invalid collection"), 404
            
        pdf_text = safe_pdf_extraction(RESOURCE_URLS[collection])
        if not pdf_text:
            return render_template('error.html', message="Failed to load content"), 500
            
        return render_template(f'{collection}.html', pdf_text=pdf_text)
    except Exception as e:
        logger.error(f"Hadith Error ({collection}): {str(e)}\n{traceback.format_exc()}")
        return render_template('error.html', message="Hadith load failed"), 500

@app.route('/api/surahs')
def api_surahs():
    """API endpoint for surah list"""
    try:
        data = fetch_quran_data("surah")
        return jsonify(data['data'] if data and data.get('data') else [])
    except Exception as e:
        logger.error(f"API Surahs Error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Error: {str(error)}\n{traceback.format_exc()}")
    return render_template('error.html', message="Internal server error"), 500