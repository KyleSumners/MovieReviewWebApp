export default interface Movie {
  id: number;
  title: string;
  year: number;
  rating: number;
  director: string;
  genre: string[];
  posterUrl: string;
  description: string;
}