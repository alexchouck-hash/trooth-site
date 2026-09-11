import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://alexchouck-hash.github.io',
  base: process.env.BASE_PATH !== undefined ? process.env.BASE_PATH : '/trooth-site',
  output: 'static',
  build: {
    format: 'directory'
  }
});
