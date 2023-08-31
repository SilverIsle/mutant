from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_actor_id(api_key, actor_name):
    search_url = "https://api.themoviedb.org/3/search/person"

    params = {
        "api_key": api_key,
        "query": actor_name
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    if data['results']:
        return data['results'][0]['id']
    else:
        return None

def get_genre_id(api_key, genre_name):
    genres_url = "https://api.themoviedb.org/3/genre/movie/list"

    params = {
        "api_key": api_key,
        "language": "en-US"
    }

    response = requests.get(genres_url, params=params)
    data = response.json()

    for genre in data['genres']:
        if genre['name'].lower() == genre_name.lower():
            return genre['id']

    return None

@app.route('/')
def index():
    return render_template('index.html')

def get_movie_suggestions(api_key, num_suggestions, genre_id, actor_id, min_rating, year, language):
    discover_url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "with_cast": actor_id,
        "vote_average.gte": min_rating,
        "primary_release_year": year,
        "language": language,
        "sort_by": "popularity.desc"
    }

    if not actor_id:
        del params["with_cast"]

    response = requests.get(discover_url, params=params)
    data = response.json()

    if "results" in data:
        base_image_url = "https://image.tmdb.org/t/p/w500"
        for movie in data["results"][:num_suggestions]:
            poster_path = movie.get("poster_path", "")
            movie["poster_url"] = base_image_url + poster_path

            # Get additional details using the movie ID
            movie_details_url = f"https://api.themoviedb.org/3/movie/{movie['id']}?api_key={api_key}&append_to_response=credits&language={language}"
            details_response = requests.get(movie_details_url)
            details_data = details_response.json()
            
            movie["imdb_rating"] = details_data.get("vote_average")
            movie["main_cast"] = ", ".join([cast["name"] for cast in details_data.get("credits", {}).get("cast", [])[:3]])
            movie["duration"] = details_data.get("runtime")
            
        return data["results"][:num_suggestions]
    else:
        return []

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    api_key = "cef81653fa5eeeedc626069e5addf099"
    
    num_suggestions = int(request.form['num_suggestions'])
    genre = request.form['genre']
    actor = request.form['actor']
    rating = float(request.form['rating']) if request.form['rating'] else None
    year = request.form['year']
    language = request.form['language']
    
    actor_id = get_actor_id(api_key, actor)
    genre_id = get_genre_id(api_key, genre)
    
    movie_suggestions = get_movie_suggestions(api_key, num_suggestions, genre_id, actor_id, rating, year, language)
    
    return render_template('index.html', suggestions=movie_suggestions)

if __name__ == '__main__':
    app.run(debug=True)
