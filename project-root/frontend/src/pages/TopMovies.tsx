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

interface Movie {
  id: number;
  title: string;
  year: number;
  rating: number;
  director: string;
  genre: string[];
  posterUrl: string;
  description: string;
}

const TopMovies = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

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
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'scale(1.02)',
                },
              }}
            >
              <CardMedia
                component="img"
                height="300"
                image={movie.posterUrl}
                alt={movie.title}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h6" component="h2">
                  {movie.title}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  Released: {movie.year} | Rating: {movie.rating.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Director: {movie.director}
                </Typography>
                <Box sx={{ mb: 1 }}>
                  {movie.genre.map((g) => (
                    <Chip
                      key={g}
                      label={g}
                      size="small"
                      sx={{ mr: 0.5, mb: 0.5 }}
                    />
                  ))}
                </Box>
                <Rating 
                  value={movie.rating / 2} 
                  precision={0.1} 
                  readOnly 
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {movie.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default TopMovies; 