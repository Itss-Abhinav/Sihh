import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, '../dist');

if (fs.existsSync(path.join(distDir, 'index.html'))) {
  const indexHtml = fs.readFileSync(path.join(distDir, 'index.html'), 'utf-8');
  
  // 1. Write 404.html fallback
  fs.writeFileSync(path.join(distDir, '404.html'), indexHtml);
  
  // 2. Write dist/vercel.json rewrite configuration
  const vercelConfig = {
    rewrites: [
      { source: '/(.*)', destination: '/index.html' }
    ]
  };
  fs.writeFileSync(path.join(distDir, 'vercel.json'), JSON.stringify(vercelConfig, null, 2));

  // 3. Pre-generate physical routes for all SPA pages
  const routes = ['scan', 'login', 'register', 'history', 'admin', 'report', 'rules'];
  for (const r of routes) {
    const rDir = path.join(distDir, r);
    if (!fs.existsSync(rDir)) {
      fs.mkdirSync(rDir, { recursive: true });
    }
    fs.writeFileSync(path.join(rDir, 'index.html'), indexHtml);
  }
  console.log('✓ SPA static route fallbacks and dist/vercel.json successfully generated in dist/');
}