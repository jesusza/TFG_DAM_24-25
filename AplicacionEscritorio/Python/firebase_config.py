import firebase_admin
from firebase_admin import credentials, firestore, auth

# Cargar las credenciales de Firebase desde el archivo JSON
cred = credentials.Certificate("gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json")
firebase_admin.initialize_app(cred)

# Inicializar Firestore
db = firestore.client()

print("✅ Firebase configurado correctamente en Python.")
