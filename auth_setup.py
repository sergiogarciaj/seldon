import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Public Client ID for gcloud SDK (from Radar)
CLIENT_CONFIG = {
    "installed": {
        "client_id": "32555940559.apps.googleusercontent.com",
        "client_secret": "ZmssLNjJy2998hD4CTg2ejr2",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive'
]

def run_auth():
    print("Iniciando flujo de autenticación para BigQuery...")
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    
    # Use localhost redirect for manual copy-paste from URL bar
    flow.redirect_uri = 'http://localhost:8085/'
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n⚠️  Por favor visita esta URL en tu navegador:\n")
    print(auth_url)
    print("\n")
    
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = input("Introduzca el código de autorización: ")
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    try:
        with open('credentials.json', 'w') as f:
            f.write(creds.to_json())
        print("\n✅ Credenciales guardadas exitosamente en credentials.json")
        print("Ahora puedes ejecutar 'python main.py' para obtener datos.")
    except Exception as e:
        print(f"\n⚠️ No se pudo escribir en el archivo: {e}")

if __name__ == "__main__":
    run_auth()
