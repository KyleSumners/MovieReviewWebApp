import traceback
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import get_db, init_db
from src.models import Movie, Review, ReviewDTO
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    init_db()

# IMDb Top 100 URL
IMDB_URL = "https://www.imdb.com/chart/top/"
RATE_LIMIT_DELAY = 1  # Delay between requests in seconds

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "API is running"}

@app.get("/api/check-db")
async def check_db(db: Session = Depends(get_db)):
    """Check database connection."""
    try:
        # Try a simple query
        result = db.execute("SELECT 1").fetchone()
        return {"status": "Database connected", "result": result[0]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def fetch_movie_details(movie_url: str, index: int) -> Dict:
    """Fetch detailed information for a single movie."""
    try:
        print(f"\nProcessing movie {index+1}/100: {movie_url}")
        
        # Add delay to avoid rate limiting
        await asyncio.sleep(RATE_LIMIT_DELAY)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(movie_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Print the HTML structure
        print(f"\nFetching details for: {movie_url}")
        
        # Extract movie details
        title_element = soup.find('h1', {'data-testid': 'hero__pageTitle'})
        title = title_element.text.strip() if title_element else "Unknown Title"
        print(f"Found title: {title}")
        
        # Get year - try multiple selectors
        year = 0
        # Try metadata list first
        metadata_list = soup.select('ul[data-testid="hero-title-block__metadata"] li')
        if metadata_list:
            for item in metadata_list:
                text = item.text.strip()
                if re.search(r'\d{4}', text):
                    year = int(re.search(r'\d{4}', text).group(0))
                    break
        
        # If year not found, try other selectors
        if year == 0:
            year_selectors = [
                'span.sc-c0dd5f56-1',
                'a.ipc-link.ipc-link--baseAlt.ipc-link--inherit-color',
                '[class*="TitleBlockMetaData__MetaDataText"]',
                '[data-testid="title-details-releasedate"]'
            ]
            for selector in year_selectors:
                year_element = soup.select_one(selector)
                if year_element and re.search(r'\d{4}', year_element.text):
                    year = int(re.search(r'\d{4}', year_element.text).group(0))
                    break
        
        print(f"Found year: {year}")
        
        # Get rating
        rating_element = soup.find('span', {'class': 'sc-bde20123-1'})
        if not rating_element:
            rating_element = soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
        rating_text = rating_element.text if rating_element else "0.0"
        rating = float(re.search(r'\d+\.\d+', rating_text).group(0)) if re.search(r'\d+\.\d+', rating_text) else 0.0
        print(f"Found rating: {rating}")
        
        # Get director
        director_element = soup.find('a', {'class': 'ipc-metadata-list-item__list-content-item'})
        if not director_element:
            director_element = soup.select_one('[data-testid="title-pc-principal-credit"]:first-child a')
        director = director_element.text if director_element else "Unknown"
        print(f"Found director: {director}")
        
        # Get genres
        genre_elements = soup.find_all('a', {'class': 'ipc-chip'})
        if not genre_elements:
            genre_elements = soup.select('[data-testid="genres"] a')
        genres = [genre.text for genre in genre_elements]
        print(f"Found genres: {genres}")
        
        # Get description
        description_element = soup.find('span', {'data-testid': 'plot-xl'})
        if not description_element:
            description_element = soup.select_one('[data-testid="plot-l"]')
        if not description_element:
            description_element = soup.select_one('[data-testid="storyline-plot-summary"]')
        description = description_element.text if description_element else "No description available."
        print(f"Found description: {description[:100]}...")
        
        # Get poster URL
        poster_element = soup.find('img', {'class': 'ipc-image'})
        if not poster_element:
            poster_element = soup.select_one('div[data-testid="hero-media__poster"] img')
        poster_url = poster_element['src'] if poster_element else None
        print(f"Found poster URL: {poster_url}")
        
        print(f"Successfully processed: {title} ({year})")
        
        return {
            "id": movie_url.split('/')[-2],
            "title": title,
            "year": year,
            "rating": rating,
            "director": director,
            "genre": genres,
            "description": description,
            "posterUrl": poster_url
        }
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        traceback.print_exc()
        return None

async def fetch_and_cache_movies(db: Session):
    """Fetch movies from IMDb and cache them in the database."""
    try:
        print("\nStarting to fetch top 100 movies from IMDb...")
        start_time = time.time()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(IMDB_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different selectors for movie list
        movie_elements = soup.select('tbody.ipc-metadata-list-item__content-group tr')
        if not movie_elements:
            movie_elements = soup.find_all('li', {'class': 'ipc-metadata-list-summary-item'})
        if not movie_elements:
            movie_elements = soup.select('.cli-children [data-testid="chart-layout-main-column"]')
        
        # Ensure we only process the first 100 movies
        movie_elements = movie_elements[:100]
        total_movies = len(movie_elements)
        print(f"Found {total_movies} movies to process")
        
        for index, element in enumerate(movie_elements):
            # Try different ways to get the movie URL
            link = element.find('a', {'class': 'ipc-title-link-wrapper'})
            if not link:
                link = element.select_one('a[data-testid="title-details-link"]')
            if not link:
                link = element.select_one('a[class*="TitleLink"]')
            
            if link:
                href = link.get('href', '')
                if href:
                    if not href.startswith('http'):
                        movie_url = f"https://www.imdb.com{href}"
                    else:
                        movie_url = href
                    
                    movie_data = await fetch_movie_details(movie_url, index)
                    if movie_data:
                        # Update or create movie in database
                        movie = Movie(
                            id=movie_data["id"],
                            title=movie_data["title"],
                            year=movie_data["year"],
                            rating=movie_data["rating"],
                            director=movie_data["director"],
                            genre=movie_data["genre"],
                            description=movie_data["description"],
                            poster_url=movie_data["posterUrl"],
                            last_updated=datetime.utcnow()
                        )
                        db.merge(movie)  # merge will update if exists, insert if not
        
        db.commit()
        end_time = time.time()
        duration = end_time - start_time
        print(f"\nFinished processing all movies in {duration:.2f} seconds")
        return True
    except Exception as e:
        print(f"Error fetching top movies: {e}")
        traceback.print_exc()
        db.rollback()
        return False

def should_update_cache(db: Session) -> bool:
    """Check if the cache needs to be updated."""
    # Only update if there are no movies in the database
    movie_count = db.query(Movie).count()
    return movie_count == 0

@app.get("/api/movies/refresh")
async def refresh_movies(db: Session = Depends(get_db)):
    """Endpoint to force refresh the movie cache."""
    try:
        success = await fetch_and_cache_movies(db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update movie cache")
        return {"message": "Movie cache refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh movies: {str(e)}")

@app.get("/api/movies/top-100")
async def get_top_movies(db: Session = Depends(get_db)):
    """Endpoint to get the top 100 movies."""
    try:
        # Only fetch new data if the database is empty
        if should_update_cache(db):
            print("Database empty, fetching initial data...")
            try:
                success = await fetch_and_cache_movies(db)
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to update movie cache")
            except Exception as fetch_error:
                print(f"Detailed fetch error: {str(fetch_error)}")
                raise HTTPException(status_code=500, detail=f"Error scraping movies: {str(fetch_error)}")
        
        # Get movies from cache
        try:
            movies = db.query(Movie).order_by(Movie.rating.desc()).all()
            if not movies:
                print("No movies found in database")
                return []
            return [movie.to_dict() for movie in movies]
        except Exception as db_error:
            print(f"Database query error: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        print(f"Detailed error in get_top_movies: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch movies: {str(e)}")

@app.get("/api/stats/genres")
async def get_genre_stats(db: Session = Depends(get_db)):
    """Endpoint to get genre statistics."""
    movies = db.query(Movie).all()
    genre_stats = {}
    
    for movie in movies:
        for genre in movie.genre:
            if genre not in genre_stats:
                genre_stats[genre] = {'count': 0, 'total_rating': 0}
            genre_stats[genre]['count'] += 1
            genre_stats[genre]['total_rating'] += movie.rating
    
    return [
        {
            'genre': genre,
            'count': stats['count'],
            'averageRating': round(stats['total_rating'] / stats['count'], 1)
        }
        for genre, stats in genre_stats.items()
    ]

@app.get("/api/stats/years")
async def get_year_stats(db: Session = Depends(get_db)):
    """Endpoint to get year statistics."""
    movies = db.query(Movie).all()
    year_stats = {}
    
    for movie in movies:
        year = movie.year
        if year not in year_stats:
            year_stats[year] = {'count': 0, 'total_rating': 0}
        year_stats[year]['count'] += 1
        year_stats[year]['total_rating'] += movie.rating
    
    return [
        {
            'year': year,
            'count': stats['count'],
            'averageRating': round(stats['total_rating'] / stats['count'], 1)
        }
        for year, stats in sorted(year_stats.items(), reverse=True)
    ]

@app.get("/api/stats/directors")
async def get_director_stats(db: Session = Depends(get_db)):
    """Endpoint to get director statistics."""
    movies = db.query(Movie).all()
    director_stats = {}
    
    for movie in movies:
        director = movie.director
        if director not in director_stats:
            director_stats[director] = {'count': 0, 'total_rating': 0}
        director_stats[director]['count'] += 1
        director_stats[director]['total_rating'] += movie.rating
    
    return [
        {
            'director': director,
            'movieCount': stats['count'],
            'averageRating': round(stats['total_rating'] / stats['count'], 1)
        }
        for director, stats in sorted(director_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    ]

@app.get("/api/movies/{movie_id}")
async def get_movie_by_id(movie_id: str, db: Session = Depends(get_db)):
    """Endpoint to fetch the details of a specific movie"""
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        return movie.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving movie details: {str(e)}")

@app.get("/api/movies/{movie_id}/reviews")
def get_reviews(movie_id: str, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    return [review.to_dict() for review in reviews]


@app.post("/api/movies/{movie_id}/review")
def add_review(movie_id: str, review: ReviewDTO, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    review = Review(movie_id=movie_id, rating=review.rating, review_msg=review.review_msg)
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"message": "Review added successfully", "review": review}


@app.get("/api/movies/demo")
async def get_demo_movies():
    """Endpoint to get demo movies (fallback if scraping fails)."""
    # Static sample data
    movies = [
        {
            "id": "tt0111161",
            "title": "The Shawshank Redemption",
            "year": 1994,
            "rating": 9.3,
            "director": "Frank Darabont",
            "genre": ["Drama", "Crime"],
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "posterUrl": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_UY67_CR0,0,45,67_AL_.jpg"
        },
        {
            "id": "tt0068646",
            "title": "The Godfather",
            "year": 1972,
            "rating": 9.2,
            "director": "Francis Ford Coppola",
            "genre": ["Crime", "Drama"],
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "posterUrl": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UY67_CR1,0,45,67_AL_.jpg"
        },
        {
            "id": "tt0468569",
            "title": "The Dark Knight",
            "year": 2008,
            "rating": 9.0,
            "director": "Christopher Nolan",
            "genre": ["Action", "Crime", "Drama", "Thriller"],
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "posterUrl": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_UY67_CR0,0,45,67_AL_.jpg"
        }
    ]
    return movies