#!/bin/bash

set -e  # Exit on error

SITE_NAME="sg1_v4"
SITE_ROOT="/home/pi/sg1_v4/web"
NGINX_CONF="/etc/nginx/sites-available/$SITE_NAME"
NGINX_LINK="/etc/nginx/sites-enabled/$SITE_NAME"

echo "This script will migrate your system from Apache2 to Nginx and modify system services."

read -p "Are you sure you want to continue? [yes/no]: " CONFIRM
CONFIRM=$(echo "$CONFIRM" | tr '[:upper:]' '[:lower:]')
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborting migration."
    exit 1
fi

read -p "Do you want to [disable] or [remove] Apache2? [disable/remove]: " APACHE_ACTION
APACHE_ACTION=$(echo "$APACHE_ACTION" | tr '[:upper:]' '[:lower:]')

if [[ "$APACHE_ACTION" == "remove" ]]; then
    echo "Attempting to stop and remove Apache2..."

    if systemctl list-units --type=service --all | grep -q apache2.service; then
        sudo systemctl stop apache2 || true
        sudo systemctl disable apache2 || true
    else
        echo "Apache2 service not found—may already be removed."
    fi

    if dpkg -l | grep -q apache2; then
        sudo apt purge -y apache2 apache2-utils apache2-bin apache2.2-common || true
        sudo apt autoremove -y || true
    else
        echo "Apache2 packages not found—likely already removed."
    fi
elif [[ "$APACHE_ACTION" == "disable" ]]; then
    echo "Attempting to disable Apache2..."

    if systemctl list-units --type=service --all | grep -q apache2.service; then
        sudo systemctl stop apache2 || true
        sudo systemctl disable apache2 || true
    else
        echo "Apache2 service not found—already removed or not installed."
    fi
else
    echo "Invalid choice: must be 'disable' or 'remove'."
    exit 1
fi

echo "Installing Nginx..."
sudo apt update || true
sudo apt install -y nginx

echo "Changing Nginx user from www-data to pi..."
sudo sed -i 's/^user www-data;/user pi;/' /etc/nginx/nginx.conf || true

echo "Creating Nginx site config at $NGINX_CONF..."
sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    root $SITE_ROOT;
    index index.html index.htm;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location /stargate/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_http_version 1.1;
        proxy_redirect off;
    }
}
EOF

echo "Enabling the new site..."
sudo ln -sf "$NGINX_CONF" "$NGINX_LINK" || true

echo "Removing default Nginx site if it exists..."
sudo rm -f /etc/nginx/sites-enabled/default || true

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "Migration complete. Nginx is now serving your site from $SITE_ROOT"
