# Use a Node.js base image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if you have one)
# to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy the rest of your application code to the container
COPY . .

# Expose the port your app runs on. Cloud Run requires it to listen on $PORT.
# Your server.js is currently listening on 8001, let's adjust it for Cloud Run.
# We'll set the PORT environment variable in Cloud Run.
# The server.js should listen on process.env.PORT.
EXPOSE 8080 # Cloud Run generally uses 8080 by default

# Command to run your application
CMD [ "npm", "start" ]
