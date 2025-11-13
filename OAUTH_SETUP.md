# Google OAuth Setup for NYU Authentication

This guide explains how to set up Google OAuth authentication for the RMP Scraper application.

## Prerequisites

- Google Cloud Project (create one at https://console.cloud.google.com)
- Administrator access to create OAuth credentials

## Step 1: Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:5000/oauth/callback` (for local development)
     - `https://yourdomain.com/oauth/callback` (for production)
   - Click "Create"

5. Download the credentials as JSON and save as `client_secret.json` in the project root

## Step 2: Set Environment Variables

Create or update `.env` file with:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your_random_secret_key_here
OPENAI_API_KEY=your_openai_key
```

## Step 3: Configure Authorized Domains

For production deployment:

1. In Google Cloud Console > APIs & Services > OAuth Consent Screen
2. Add your domain to "Authorized domains"
3. Add your deployment URL to the redirect URIs

## Step 4: Test Locally

```bash
python app.py
# Navigate to http://localhost:5000
# Click "Sign in with Google"
# Use your @nyu.edu account
```

## Troubleshooting

### "client_secret.json not found"
- Ensure you downloaded the credentials from Google Cloud Console
- Place it in the project root directory

### "Redirect URI mismatch"
- Check that the redirect URI in Google Cloud Console matches exactly (including protocol and port)
- For Azure App Service, use `https://yourapplication.azurewebsites.net/oauth/callback`

### "Access Denied - Not NYU Account"
- Only @nyu.edu email addresses are allowed
- Contact your NYU IT administrator if you don't have an @nyu.edu account

## Security Notes

- Never commit `client_secret.json` to git (it's in `.gitignore`)
- Always use HTTPS in production
- Keep your `GOOGLE_CLIENT_SECRET` confidential
- Store all secrets in environment variables, never hardcode them
