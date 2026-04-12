from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import requests

RAWG_API_KEY = "2c9b69b3cf574fd687bec9d469f85c33"

app=Flask(__name__)

app.config["MYSQL_HOST"]= 'localhost'
app.config["MYSQL_USER"]= 'rishabh'
app.config["MYSQL_PASSWORD"]= 'abc123'
app.config["MYSQL_DB"]= 'game'
app.config["UPLOAD_FOLDER"]= 'static/uploads'

mysql=MySQL(app)

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

@app.route('/test')
def test_db():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    cursor.close()
    return "Because I am Batman"

@app.route('/')
def index():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM games ORDER BY date_added desc")
    games=cursor.fetchall()
    cursor.close()
    return render_template('index.html',games=games)

@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form['title']
        rating = request.form['rating'] or None
        review = request.form['review']
        status = request.form['status']
        completionTime = request.form['completionTime'] or None

        game_data=fetch_game_data(title)
        name = None
        image_url = None
        audienceRating = None
        releaseDate=None

        if game_data:
            name = game_data["name"]
            image_url = game_data["image"]
            audienceRating = game_data["rating"]
            releaseDate = game_data["released"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO games
            (title, rating, review, status, completionTime, image_filename, audienceRating, releaseDate, date_added)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,(name,rating,review,status,completionTime,image_url,audienceRating,releaseDate,datetime.now()))

        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    return render_template('add_game.html')

@app.route('/delete/<int:id>')
def delete_game(id):
    cursor=mysql.connection.cursor()
    cursor.execute("DELETE FROM games where id = %s",(id,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_game(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

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

        cursor.execute("""
            UPDATE games
            SET title=%s,
                rating=%s,
                review=%s,
                status=%s,
                completionTime=%s,
                image_filename=%s,
                audienceRating=%s,
                releaseDate=%s
            WHERE id=%s
        """, (
            name,
            rating,
            review,
            status,
            completionTime,
            image_url,
            audienceRating,
            releaseDate,
            id
        ))

        mysql.connection.commit()
        cursor.close()

        return redirect('/')

    cursor.execute("SELECT * FROM games WHERE id=%s", (id,))
    game = cursor.fetchone()
    cursor.close()

    return render_template('edit_game.html', game=game)

@app.route('/game/<int:id>')
def game_detail(id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM games WHERE id=%s", (id,))
    game = cursor.fetchone()

    cursor.close()

    return render_template("game-details.html", game=game)

if __name__ == "__main__":
    app.run(debug=True)



