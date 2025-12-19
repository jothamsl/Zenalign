
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.append(os.getcwd())

try:
    from app.routers.payment import _ensure_services_initialized, _db_client, _interswitch_client, _token_service
    from app.services.interswitch_client import InterswitchClient
    
    print("Attempting to initialize services...")
    _ensure_services_initialized()
    
    from app.routers import payment
    
    if payment._db_client is None:
        print("ERROR: MongoDB client is None")
    else:
        print("SUCCESS: MongoDB client initialized")
        
    if payment._interswitch_client is None:
        print("ERROR: Interswitch client is None")
        # Try to initialize it manually to see the error
        try:
            print("Attempting manual InterswitchClient init...")
            client = InterswitchClient()
            print("Manual init successful")
        except Exception as e:
            print(f"Manual init failed: {e}")
    else:
        print("SUCCESS: Interswitch client initialized")
        
    if payment._token_service is None:
        print("ERROR: Token service is None")
    else:
        print("SUCCESS: Token service initialized")

except Exception as e:
    print(f"Script failed: {e}")
