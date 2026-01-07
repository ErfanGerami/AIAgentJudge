FROM nginx

# Copy custom nginx config (must have .conf extension)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set working directory for static files
WORKDIR /usr/share/nginx/html

# Copy all frontend files into Nginx html folder
COPY . .

# Expose port 80
EXPOSE 80

# Start Nginx (optional, base image already does this)
# CMD ["nginx", "-g", "daemon off;"]
