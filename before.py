from flask import Flask, render_template,request,jsonify, redirect, url_for
import requests
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = {}
HADITH_API_KEY = "$2y$10$yN5HfnnlJ0gz9PyW36P7ezfHT3u0p9BwhGNylP54T0BmL5ZbU7K" 
HADITH_API_BASE_URL = "https://hadithapi.com/api"
def fetch_hijri_calendar(date=None):
    """Fetch Hijri calendar data from Aladhan API"""
    base_url = "https://api.aladhan.com/v1/gToH"
    params = {
        'date': date if date else 'today',  # Default to today's date
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        print(f"Response: {response.json()}")  # Debug log
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hijri calendar data: {e}")
        return None
    

def fetch_hadith_data(endpoint, params=None):
    """Fetch data from Hadith API"""
    if params is None:
        params = {}
    
    # Add API key to params
    params['apiKey'] = HADITH_API_KEY
    
    url = f"{HADITH_API_BASE_URL}/{endpoint}"
    print(f"Fetching data from URL: {url} with params: {params}")  # Debug log
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        try:
            return response.json()
        except ValueError:
            print("Error: Response is not in JSON format")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request error: {str(e)}")  # Debug log
        return None

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
    hijri_data = fetch_hijri_calendar()
    if data and data.get('data') and hijri_data and hijri_data.get('data'):
        return render_template('index.html', surahs=data['data'],hijri_date=hijri_data['data'])
    return "Error fetching Surah list", 500

@app.route('/generic')
def generic():
    return render_template('generic.html')

@app.route('/elements')
def elements():
    return render_template('elements.html')

@app.route('/surah/<int:surah_number>')
def get_surah(surah_number):
    data = get_quran_data(f"surah/{surah_number}/en.sahih")
    if data and data.get('data'):
        return render_template('surah.html', surah=data['data'])
    return "Error fetching Surah data", 500
@app.route('/hadiths')
def hadith_collections():
    # Fetch Hadith collections
    collections = fetch_hadith_data("collections")
    if collections and collections.get('data'):
        return render_template('hadith_collections.html', collections=collections['data'])
    return "Error fetching Hadith collections", 500

@app.route('/hadiths/<collection_name>')
def hadith_books(collection_name):
    # Fetch books from the selected collection
    books = fetch_hadith_data(f"collections/{collection_name}/books")
    if books and books.get('data'):
        return render_template('hadith_books.html', books=books['data'], collection_name=collection_name)
    return "Error fetching books for the collection", 500

@app.route('/hadiths/<collection_name>/<int:book_number>')
def hadiths_in_book(collection_name, book_number):
    # Get the page and limit from query parameters (default to page 1, 10 items per page)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Fetch Hadiths from the selected book with pagination
    hadiths = fetch_hadith_data(f"collections/{collection_name}/books/{book_number}/hadiths", params={'page': page, 'limit': limit})
    if hadiths and hadiths.get('data'):
        return render_template(
            'hadiths.html',
            hadiths=hadiths['data'],
            collection_name=collection_name,
            book_number=book_number,
            page=page,
            total_pages=hadiths.get('totalPages', 1)  # Assuming the API provides total pages
        )
    return "Error fetching Hadiths for the book", 500
@app.route('/calendar')
def islamic_calendar():
    hijri_data = fetch_hijri_calendar()
    if hijri_data and hijri_data.get('data'):
        print(f"Hijri Data: {hijri_data}")  # Debug log
        return render_template('calendar.html', hijri_date=hijri_data['data'])
    return "Error fetching Hijri calendar data", 500

if __name__ == '__main__':