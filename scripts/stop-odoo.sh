#!/bin/bash

echo "🛑 Stopping Odoo ERP System..."
echo ""

# Stop Odoo container
echo "📦 Stopping Odoo container..."
docker stop odoo
echo "✅ Odoo container stopped"

# Stop database container
echo "📦 Stopping database container..."
docker stop odoo-db
echo "✅ Database container stopped"

echo ""
echo "✅ Odoo system stopped successfully!"
echo ""
echo "💡 To start again, run: ./scripts/start-odoo.sh"
