"""
Development server entry point for FlagDojo.
Run this file to start the application in development mode.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
