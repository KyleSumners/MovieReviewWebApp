from sqlalchemy import Column, Integer, String, Float, DateTime, Table, ForeignKey, create_engine, ARRAY
from datetime import datetime

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