from flask import Flask, render_template,request,jsonify, redirect, url_for
import requests
import PyPDF2


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = {}

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text
def get_quran_data(endpoint, params=None):
    base_url = "https://api.alquran.cloud/v1/"
    try:
        response = requests.get(base_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None


@app.route('/search')
def search_quran():
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', error="Please enter a search term")
    
    # Make the API search request
    search_params = {
        'q': query,
        'language': 'en',
        'surah': request.args.get('surah', ''),
        'offset': request.args.get('offset', 0),
        'limit': 20  # Limit results per page
    }
    
    search_data = get_quran_data("search", params=search_params)
    
    if not search_data or not search_data.get('data'):
        return render_template('search.html', 
                           error="No results found",
                           query=query)
    
    # Get surah names for display
    surahs_data = get_quran_data("surah")
    surahs_map = {s['number']: s for s in surahs_data['data']} if surahs_data else {}
    
    # Process search results
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
    
    # Pagination info
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
                         surahs=surah_data['data'] if surahs_data else [])

# Route to get all surahs (for dropdown)
@app.route('/api/surahs')
def get_surahs():
    surahs_data = get_quran_data("surah")
    return jsonify(surahs_data['data']) if surahs_data else jsonify([])
@app.route('/')
def home():
    # Get list of all surahs
    data = get_quran_data("surah")
    if data and data.get('data'):
        return render_template('index.html', surahs=data['data'],)
    return "Error fetching Surah list", 500



@app.route('/bukhari')
def bukhari():
    # Path to the PDF file
    pdf_path = "static/pdfs/bukhari.pdf"
    
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if not pdf_text:
        return "Error extracting text from the PDF", 500
    
    # Render the text in an HTML template
    return render_template('bukhari.html', pdf_text=pdf_text)


@app.route('/tirmidhi')
def tirmidhi():
    # Path to the PDF file
    pdf_path = "static/pdfs/tirmidhi.pdf"
    
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if not pdf_text:
        return "Error extracting text from the PDF", 500
    
    # Render the text in an HTML template
    return render_template('tirmidhi.html', pdf_text=pdf_text)


@app.route('/surah/<int:surah_number>')
def get_surah(surah_number):
    data = get_quran_data(f"surah/{surah_number}/en.sahih")
    if data and data.get('data'):
        return render_template('surah.html', surah=data['data'])
    return "Error fetching Surah data", 500


@app.route('/muslim')
def muslim():
    # Path to the PDF file
    pdf_path = "static/pdfs/muslim.pdf"
    
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if not pdf_text:
        return "Error extracting text from the PDF", 500
    
    # Render the text in an HTML template
    return render_template('muslim.html', pdf_text=pdf_text)


if __name__ == '__main__':
    app.run(debug=True)