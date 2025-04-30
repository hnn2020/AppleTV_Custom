#!/usr/bin/env python3
"""
Example script demonstrating the swipe functionality in pyatv.
Based on the pyatv scan_and_connect.py example.
"""

import asyncio
import sys
from typing import Dict, Optional

import pyatv


async def swipe_example(ip_address: Optional[str] = None) -> None:
    """Connect to an Apple TV and perform swipe actions."""
    print("Starting discovery...")
    atvs = await pyatv.scan(identifier=ip_address)
    
    if not atvs:
        print("No device found")
        return

    print(f"Found {len(atvs)} Apple TV(s)")
    
    # Use the first Apple TV found if no IP address specified
    device = atvs[0]
    
    print(f"Connecting to {device.name} ({device.address})...")
    
    atv = await pyatv.connect(device, protocol=pyatv.Protocol.MRP)
    
    try:
        print("Connected! Ready to perform swipe operations.")
        print("Available commands: left, right, up, down, exit")
        
        while True:
            command = input("Enter command: ").strip().lower()
            
            if command == "exit":
                break
                
            # Map commands to dx/dy values
            swipe_params: Dict[str, tuple] = {
                "left": (-0.5, 0),
                "right": (0.5, 0),
                "up": (0, -0.5),
                "down": (0, 0.5),
            }
            
            if command in swipe_params:
                dx, dy = swipe_params[command]
                print(f"Swiping {command} (dx={dx}, dy={dy})...")
                await atv.remote_control.swipe(dx, dy)
            else:
                print(f"Unknown command: {command}")
    
    finally:
        print("Closing connection...")
        atv.close()


if __name__ == "__main__":
    # Accept an optional IP address as a command-line parameter
    ip_address = sys.argv[1] if len(sys.argv) > 1 else None
    
    asyncio.run(swipe_example(ip_address)) 