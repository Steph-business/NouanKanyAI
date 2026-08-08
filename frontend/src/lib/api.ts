// Base URL de l'API backend FastAPI.
// En local: http://localhost:8000 (valeur par défaut).
// En production sur Render: définir NEXT_PUBLIC_API_URL dans les variables d'environnement du service frontend.
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const API_URL = rawApiUrl.replace(/\/$/, '');
