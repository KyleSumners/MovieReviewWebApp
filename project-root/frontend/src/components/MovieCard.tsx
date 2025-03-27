import React from 'react';
import { Card,
    CardMedia,
    CardContent,
    Typography,
    Box,
    Chip,
    Rating
} from '@mui/material';

const MovieCard = ({movie, small = false}) => {
    return (
        <Card
            sx={{
                height: small ? '100%' : 'auto',
                display: 'flex',
                flexDirection: small ? 'column' : 'row',
                transition: 'transform 0.2s',
                '&:hover': {
                    transform: 'scale(1.02)',
                },
            }}
        >
            <CardMedia
                component="img"
                height={small ? '300' : '450'}
                sx={small ? {} : { width: 300, height: 450 }}
                image={movie.posterUrl}
                alt={movie.title}
              />
            <CardContent>
                <Typography gutterBottom variant={small ? 'h6' : 'h4'} component="h2">
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
                {!small && (
                    <Typography variant="body2" color="text.secondary">
                        {movie.description}
                    </Typography>
                )}
            </CardContent>
        </Card>
    )
}

export default MovieCard;