import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  CircularProgress,
  Rating,
  Chip,
  TextField,
  InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';
import Movie from '../interfaces/MovieInterface'
import MovieCard from "../components/MovieCard.tsx";
import { useNavigate } from 'react-router-dom';

const TopMovies = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleMovieClick = (id: number) => {
    navigate(`/movie/${id}`);
  };

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/movies/top-100`);
        setMovies(response.data);
      } catch (err) {
        console.error('Error fetching movies from main endpoint:', err);
        try {
          // Try the demo endpoint as fallback
          console.log('Trying demo endpoint...');
          const demoResponse = await axios.get(`${process.env.REACT_APP_API_URL}/api/movies/demo`);
          setMovies(demoResponse.data);
        } catch (demoErr) {
          setError('Failed to fetch movies. Please try again later.');
          console.error('Error fetching demo movies:', demoErr);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, []);

  const filteredMovies = movies.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.director.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography color="error" align="center">{error}</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        IMDb Top 100 Movies
      </Typography>

      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search movies by title or director..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 4 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      <Grid container spacing={4}>
        {filteredMovies.map((movie) => (
            <Grid item xs={12} sm={6} md={4} key={movie.id}>
                <Box
                    onClick={() => navigate(`/movie/${movie.id}`)}
                    style={{cursor: 'pointer'}}
                >
                  <MovieCard movie={movie} small/>
                </Box>
            </Grid>
          ))}
      </Grid>
    </Container>
);
};

export default TopMovies; 