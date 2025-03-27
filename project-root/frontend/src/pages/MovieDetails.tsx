import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container,
    Typography,
    CircularProgress,
    Box,
    Card,
    CardMedia,
    CardContent,
    Rating,
    Chip
} from '@mui/material';
import axios from 'axios';
import MovieCard from '../components/MovieCard.tsx'

const MovieDetails = () => {
    const { movieId } = useParams();
    const [ movie, setMovie ] = useState(null);
    const [ loading, setLoading ] = useState(true);
    const [err, setErr] = useState(null);
    // Execute only when the movieId is changed, fetches movie details
    // from our backend
    const fetchMovie = async () => {
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_URL}/api/movies/${movieId}`
            );
            setMovie(response.data);
        } catch (err) {
            console.log("Couldn't fetch movie details: ", err);
            setErr("Couldn't fetch movie details");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchMovie();
    }, [movieId]);

    // First check if we have gotten a response from our backend
    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                <CircularProgress/>
            </Box>
        )
    }

    // Then see if there was an error retrieving the movie
    if (err) {
        return (
            <Box display="flex" justifyContent="center">
                <Typography color="error" align="center">{err}</Typography>
            </Box>
        )
    }

    // Now process and display the movie details
    if (!movie) {
        return null
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
            <MovieCard movie={movie} />
        </Container>
    )
}

export default MovieDetails