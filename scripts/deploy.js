import { execSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const distDir = path.join(rootDir, 'dist');

console.log('Building site...');
execSync('npm run build', { cwd: rootDir, stdio: 'inherit' });

console.log('Deploying to gh-pages...');
const gitDir = path.join(distDir, '.git');
if (fs.existsSync(gitDir)) {
  fs.rmSync(gitDir, { recursive: true, force: true });
}

execSync('git init', { cwd: distDir, stdio: 'inherit' });
execSync('git config user.name "Alex Houck"', { cwd: distDir, stdio: 'inherit' });
execSync('git config user.email "alex.c.houck@gmail.com"', { cwd: distDir, stdio: 'inherit' });
execSync('git checkout -B gh-pages', { cwd: distDir, stdio: 'inherit' });
execSync('git add -A', { cwd: distDir, stdio: 'inherit' });
execSync('git commit -m "Deploy Trooth public site to GitHub Pages"', { cwd: distDir, stdio: 'inherit' });
execSync('git push -f https://github.com/alexchouck-hash/trooth-site.git gh-pages', { cwd: distDir, stdio: 'inherit' });
fs.rmSync(gitDir, { recursive: true, force: true });

console.log('Deployment complete!');
