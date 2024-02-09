# Dependencies
- docker
- docker-compose

# Running the Spaghetti Server
- Copy `example.env` to `.env` and fill out the values
- Run `make`, or just `docker-compose up -d --build`
- The server is running over plain HTTP, it's highly recommended to configure a reverse proxy such as nginx to enable TLS
