# MovieReviewWebApp 

1. We can create a movie database. This would be similar to rotten tomatoes, in where we fill the page with existing movies and allow users to rate/review them. Users would have the capabilities of adding and displaying movies as their favorites, reviewing, and rating movies. This would be displayed to other users, and allow them to connect to each other as well.

2. Movie enthusiasts would use it, along with friends who are trying to send movie recommendations in mass.

3. Each movie will need data such as the name, director, year released, and genre. We can obtain this by webscraping the iMDB.

4. It will need a UI to allow users to rate and display movies. It will also need a database in order to hold all these movies, as well as a backend API to keep up to date with movies that are newly released.

**Project Description**
This is a full-stack web application that allows users to explore a wide selection of popular movies! Users can find movies through a search system or by browsing top-rated films based on critical reviews. Users are also able to search for movies filmed by a certain director. Once a user has found a movie that interests them they are able to open up its movie page which features the film poster, director and any additional details about the movie. Currently there are no user accounts or authentication, and ratings are purely based off of the IMDb ratings that are scraped for data.

**Project Run Instructions**
Start the service via Docker Compose and build containers: 
i.e. docker compose up --build

Run the service after running it previously but had kept container state:
i.e. docker compose start
     
Stop the service via Docker Compose and close containers: 
i.e. docker compose down

Stop the service via Docker Compose but do not keep the state of the container:
i.e. docker compose stop

**Ports Utilized and Accessing Service**
Port 3000: React frontend
Port 8000: FastAPI backend
Port 5432: PostgreSQL database

Frontend Access: http://localhost:3000
