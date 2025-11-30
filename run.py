#!/usr/bin/env python
"""
Local Host Dashboard - Raspberry Pi System Monitoring
Main entry point for the Flask application
"""

import os
import sys
import argparse
from app import create_app

def main():
    parser = argparse.ArgumentParser(description='Local Host Dashboard for Raspberry Pi')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5002, help='Port to bind to (default: 5002)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    app = create_app()
    
    print(f"\n{'='*60}")
    print("Local Host Dashboard - Raspberry Pi System Monitor")
    print(f"{'='*60}")
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    print("Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
