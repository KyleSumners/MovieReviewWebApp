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
    Chip,
    TextField,
    Button
} from '@mui/material';
import axios from 'axios';
import MovieCard from '../components/MovieCard.tsx'

const MovieDetails = () => {
    const { movieId } = useParams();
    const [ movie, setMovie ] = useState(null);
    const [ loading, setLoading ] = useState(true);
    const [ err, setErr ] = useState(null);
    const [ reviews, setReviews ] = useState([]);
    const [ rating, setRating ] = useState(0.0);
    const [ reviewMsg, setReviewMsg] = useState("");
    const [ reviewSubmitting, setReviewSubmitting ] = useState(false);

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
    };

    const fetchReviews = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/movies/${movieId}/reviews`);
            setReviews(response.data);
        } catch (err) {
            console.log("Couldn't fetch reviews: ", err);
            setErr("Couldn't fetch reviews");
        }
    };

    const submitReview = async () => {
        setReviewSubmitting(true);
        try {
            const scaledRating = rating * 2;
            await axios.post(
                `${process.env.REACT_APP_API_URL}/api/movies/${movieId}/review`,
                {
                    rating: scaledRating,
                    review_msg: reviewMsg
                });
            setReviewMsg("");
            setRating(0.0);
            fetchReviews();
        } catch (err) {
            console.log("Couldn't submit review: ", err)
        } finally {
            setReviewSubmitting(false);
        }
    }

    useEffect(() => {
        fetchMovie();
        fetchReviews();
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
            <Box mt={4}>
                {reviews.map((review) => (
                    <Box key={review.id} mb={2}>
                        <Typography variant="body1">{review.review_msg}</Typography>
                        <Rating value={review.rating / 2} precision={0.1} readOnly />
                    </Box>
                ))}
            </Box>
            <Box mt={2}>
                <Typography variant="h6">Add a Review</Typography>
                <TextField
                    label="Your review"
                    multiline
                    rows={4}
                    fullWidth
                    value={reviewMsg}
                    onChange={(e) => setReviewMsg(e.target.value)}
                />
                <Rating
                    value={rating}
                    onChange={(e, newVal) => setRating(newVal)}
                    precision={0.5}
                    sx={{ mt: 1 }}
                />
                <Box>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={submitReview}
                        disabled={reviewSubmitting}
                    >
                        {reviewSubmitting ? "Submitting..." : "Submit Review"}
                    </Button>
                </Box>
            </Box>
        </Container>
    )
}

export default MovieDetails