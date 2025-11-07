#!/bin/bash

# Quick start script for Senalign Dataset Quality Validator

echo "=========================================="
echo "Senalign Dataset Quality Validator"
echo "=========================================="
echo ""

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY is not set!"
    echo "LLM analysis will fail without this key."
    echo ""
    echo "Set it with:"
    echo "  export OPENAI_API_KEY=your_openai_key_here"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ OPENAI_API_KEY is set"
fi

echo ""
echo "Starting server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --reload --port 8000
