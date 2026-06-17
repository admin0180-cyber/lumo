#!/bin/bash
echo "=== Lumo Setup ==="
cd "$(dirname "$0")/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo ""
echo "✅ Pronto! Para rodar:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   Depois abra frontend/index.html no navegador"
