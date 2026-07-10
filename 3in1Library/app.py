import os
import sqlite3
from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify

RAWG_API_KEY = "2c9b69b3cf574fd687bec9d469f85c33"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = 'static/uploads'

# --- Media Configurations ---
BOOKS_DIR = os.path.join(app.static_folder, 'books')
MUSIC_DIR = os.path.join(app.static_folder, 'music')

os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

# --- SQLite Database Setup ---
DB_FILE = 'library.db'

def init_db():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Existing games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            rating INTEGER,
            review TEXT,
            status TEXT,
            completionTime INTEGER,
            image_filename TEXT,
            audienceRating REAL,
            releaseDate TEXT,
            date_added TIMESTAMP
        )
    ''')
    
    # NEW: Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            filename TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            cover_url TEXT,
            current_page INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

# Run the DB setup once when the app starts
init_db()

def get_db_connection():
    """Opens a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    # This allows us to access columns by name (e.g., game['title'])
    conn.row_factory = sqlite3.Row
    return conn

# --- API Helper ---
def fetch_game_data(title):
    url = f"https://api.rawg.io/api/games?search={title}&key={RAWG_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["results"]:
        game = data["results"][0]
        return {
            "name": game["name"],
            "image": game["background_image"],
            "rating": game["rating"],
            "released": game["released"]
        }
    return None

def fetch_book_metadata(filename):
    # Clean the filename (e.g., "dune_part_1.pdf" -> "dune part 1")
    clean_title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
    url = f"https://openlibrary.org/search.json?q={clean_title}&limit=1"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("docs"):
            book = data["docs"][0]
            # Open Library provides cover images via a separate URL structure using the cover_i ID
            cover_id = book.get("cover_i")
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None

            return {
                "title": book.get("title", clean_title.title()),
                "author": book.get("author_name", ["Unknown"])[0],
                "cover": cover_url
            }
    except Exception as e:
        print(f"Error fetching metadata for {filename}: {e}")

    # Fallback if API fails or book isn't found
    return {"title": clean_title.title(), "author": "Unknown", "cover": None}

# --- Routes ---

@app.route('/')
def index():
    return render_template('hub.html')

@app.route('/games')
def games():
    conn = get_db_connection()
    games = conn.execute('SELECT * FROM games ORDER BY date_added DESC').fetchall()
    conn.close()
    return render_template('games.html', games=games)

@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating'] or None
        review = request.form['review']
        status = request.form['status']
        completionTime = request.form['completionTime'] or None

        game_data = fetch_game_data(title)
        name = None
        image_url = None
        audienceRating = None
        releaseDate = None

        if game_data:
            name = game_data["name"]
            image_url = game_data["image"]
            audienceRating = game_data["rating"]
            releaseDate = game_data["released"]

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO games 
            (title, rating, review, status, completionTime, image_filename, audienceRating, releaseDate, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, rating, review, status, completionTime, image_url, audienceRating, releaseDate, datetime.now()))
        
        conn.commit()
        conn.close()

        return redirect('/games')

    return render_template('add_game.html')

@app.route('/delete/<int:id>')
def delete_game(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM games WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/games')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_game(id):
    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating'] or None
        review = request.form['review']
        status = request.form['status']
        completionTime = request.form['completionTime'] or None

        game_data = fetch_game_data(title)
        name = title
        image_url = None
        audienceRating = None
        releaseDate = None

        if game_data:
            name = game_data["name"]
            image_url = game_data["image"]
            audienceRating = game_data["rating"]
            releaseDate = game_data["released"]

        conn.execute('''
            UPDATE games
            SET title=?, rating=?, review=?, status=?, completionTime=?, image_filename=?, audienceRating=?, releaseDate=?
            WHERE id=?
        ''', (name, rating, review, status, completionTime, image_url, audienceRating, releaseDate, id))

        conn.commit()
        conn.close()
        return redirect('/games')

    game = conn.execute('SELECT * FROM games WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_game.html', game=game)

@app.route('/game/<int:id>')
def game_detail(id):
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template("game-details.html", game=game)

@app.route('/books')
def books():
    # Get actual files currently on your hard drive
    book_files = [f for f in os.listdir(BOOKS_DIR) if f.endswith('.pdf')]
    
    conn = get_db_connection()
    
    # --- PHASE 1: Add new books ---
    for filename in book_files:
        existing = conn.execute('SELECT * FROM books WHERE filename = ?', (filename,)).fetchone()
        
        if not existing:
            meta = fetch_book_metadata(filename)
            conn.execute('''
                INSERT INTO books (filename, title, author, cover_url, current_page)
                VALUES (?, ?, ?, ?, 1)
            ''', (filename, meta['title'], meta['author'], meta['cover']))
            
    # --- PHASE 2: Cleanup deleted or renamed books ---
    # Get all filenames currently saved in the database
    db_books = conn.execute('SELECT filename FROM books').fetchall()
    
    for db_book in db_books:
        # If the database has a filename that is no longer in the folder...
        if db_book['filename'] not in book_files:
            # Delete that ghost record from the database
            conn.execute('DELETE FROM books WHERE filename = ?', (db_book['filename'],))
            
    # Commit all the additions and deletions at once
    conn.commit()
            
    # --- PHASE 3: Fetch the clean, updated list to display ---
    final_books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    
    return render_template('books.html', books=final_books)
                           
@app.route('/read/<filename>')
def read_book(filename):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE filename = ?', (filename,)).fetchone()
    conn.close()
    
    # Defensive programming: 
    # If the book was found in the DB, use its saved page. 
    # If book is None, default to page 1.
    if book:
        start_page = book['current_page']
    else:
        start_page = 1
        
    return render_template('reader.html', book_name=filename, start_page=start_page)

@app.route('/save_bookmark', methods=['POST'])
def save_bookmark():
    # This route expects a JSON payload from JavaScript
    data = request.get_json()
    filename = data.get('filename')
    page = data.get('page')
    
    if filename and page:
        conn = get_db_connection()
        conn.execute('UPDATE books SET current_page = ? WHERE filename = ?', (page, filename))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), 400

@app.route('/music')
def music():
    music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
    return render_template('music.html', songs=music_files)

if __name__ == "__main__":
    app.run(debug=True)
