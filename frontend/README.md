# FactFlow Frontend

The user interface for the PDF Fact-Check Analysis application, built with React, Vite, and Lucide icons.

## Development Setup

Run the frontend locally using the Vite development server:

```bash
# Install dependencies
npm install

# Start local development server
npm run dev
```
The app will run locally at `http://localhost:5173`.

## Production Architecture

In production, this frontend does not run a continuous Node server. Instead, it is integrated directly into the main infrastructure:

1. **Multi-Stage Build:** The root `Dockerfile` utilizes a `node:22-alpine` builder layer to compile assets.
2. **Static Asset Compilation:** Code is optimized into raw HTML, JS, and CSS files inside a `/dist` directory.
3. **Nginx Integration:** An asset exporter service drops these compiled production files into a shared Docker volume, allowing your production `nginx` container to serve them directly.

## API Connection

All backend communications use **relative routing** paths (e.g., `/api/upload/`). 

Production API requests are intercepted by Nginx on port `80` and reverse-proxied internally to the Django Gunicorn backend service. This eliminates browser CORS issues automatically.
