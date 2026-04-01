#!/bin/bash

echo "🚀 Starting Odoo ERP System..."
echo ""

# Start database container
echo "📦 Starting database container..."
docker start odoo-db
if [ $? -ne 0 ]; then
    echo "❌ Failed to start database container"
    exit 1
fi
echo "✅ Database container started"

# Wait for database to be ready
echo "⏳ Waiting for database to initialize (10 seconds)..."
sleep 10

# Start Odoo container
echo "📦 Starting Odoo container..."
docker restart odoo
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Odoo container"
    exit 1
fi
echo "✅ Odoo container restarted"

# Wait for Odoo to fully start
echo "⏳ Waiting for Odoo to fully initialize (20 seconds)..."
sleep 20

# Check if Odoo is responding
echo "🔍 Checking Odoo health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8069)

if [ "$HTTP_CODE" = "303" ] || [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "✅ SUCCESS! Odoo is running!"
    echo ""
    echo "📍 Open in browser: http://localhost:8069"
    echo ""
    echo "🔐 Login Credentials:"
    echo "   - Email: admin"
    echo "   - Password: admin"
    echo ""
    echo "💡 To stop Odoo, run: docker-compose -f docker-compose-odoo.yml down"
    echo ""
else
    echo ""
    echo "⚠️  Odoo may still be starting. Wait 30 more seconds and refresh the page."
    echo "   URL: http://localhost:8069"
fi
