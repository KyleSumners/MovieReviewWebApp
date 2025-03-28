from sqlalchemy import Column, Integer, String, Float, DateTime, Table, ForeignKey, create_engine, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel

# Import Base from database
from src.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    year = Column(Integer)
    rating = Column(Float)
    director = Column(String)
    genre = Column(ARRAY(String))
    description = Column(String)
    poster_url = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "rating": self.rating,
            "director": self.director,
            "genre": self.genre,
            "description": self.description,
            "posterUrl": self.poster_url
        }

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(String, ForeignKey("movies.id"))
    rating = Column(Float)
    review_msg = Column(String)
    movie = relationship("Movie", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "rating": self.rating,
            "review_msg": self.review_msg
        }

class ReviewDTO(BaseModel):
    rating: float
    review_msg: str