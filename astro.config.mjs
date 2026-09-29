import { defineConfig } from 'astro/config';

// SITE_URL can be set in the hosting settings (e.g. Cloudflare Pages) once a domain is chosen.
export default defineConfig({
  site: process.env.SITE_URL || 'https://kyujungjun.github.io',
  trailingSlash: 'ignore',
  redirects: { '/join': '/recruiting' },
});
