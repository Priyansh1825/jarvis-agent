#!/usr/bin/env python3
"""
====================================================================
           J.A.R.V.I.S. - CLOUD AI VOICE AGENT
              Stark Industries Mark VII Protocol
====================================================================
Hybrid Cloud Brain + Local Hands Agent for Windows Device Automation
"""

import sys
import os

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.hud import JarvisHUD
from core.server import start_mobile_server, get_local_ip

def main():
    print("=" * 60)
    print("  Initializing J.A.R.V.I.S. Mark VII Protocol...")
    print("  Cloud Brain: Gemini 2.5 Flash")
    print("  Local Hands: Windows System Automation & Media Control")
    print("  Voice Engine: Microsoft Edge Neural TTS (British Butler)")
    
    # Start Mobile Link Server
    mobile_url = start_mobile_server(port=5000)
    print(f"  📱 Mobile Phone Link: {mobile_url}")
    print("=" * 60)
    
    app = JarvisHUD()
    app.mainloop()

if __name__ == "__main__":
    main()

