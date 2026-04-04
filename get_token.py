import gkeepapi
import gpsoauth

# This uses the underlying library to get a Master Token
email = "ed@overy.nz"
password = "utljgpipmxkytedt" # Your current App Password

try:
    # 1. Get the master token
    auth = gpsoauth.perform_master_login(email, password, "android")
    master_token = auth.get('Token')
    
    if master_token:
        print("\n" + "="*60)
        print("SUCCESS! COPY THIS TOKEN:")
        print(master_token)
        print("="*60)
    else:
        print("Failed to get token. Check your App Password.")
except Exception as e:
    print(f"Error: {e}")