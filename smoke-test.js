#!/usr/bin/env node

// Lightweight production smoke test. No test runner or dependencies required.
// Usage: node smoke-test.js [site-url]

const baseUrl = (process.argv[2] || 'https://sunball-finder.pages.dev').replace(/\/$/, '');
const checks = [];

function check(label, passed, detail = '') {
  checks.push({ label, passed, detail });
  console.log(`${passed ? '✓' : '✗'} ${label}${detail ? ` — ${detail}` : ''}`);
}

async function get(path) {
  const response = await fetch(`${baseUrl}${path}`, { redirect: 'follow' });
  return { response, text: await response.text() };
}

try {
  const page = await get('/');
  check('homepage responds', page.response.ok, `${page.response.status} ${page.response.url}`);
  check('Sunball UI is present', page.text.includes('Tracey’s') && page.text.includes('Sunball Finder') && page.text.includes('A little more light; a little less cold.'));
  check('scan controls are present', page.text.includes('id="scanBtn"') && page.text.includes('id="results"'));
  check('Google hotel map links are present', page.text.includes('googleMapsPlaceUrl') && page.text.includes('Show hotels in Maps'));
  check('cannabis map links are present', page.text.includes('googleCannabisUrl') && page.text.includes('cannabis storefronts in Maps'));
  check('Google destination links are present', page.text.includes('googleHotelsUrl') && page.text.includes('googleFlightsUrl') && page.text.includes('googleMapsPlaceUrl'));
  check('flight checks are opt-in', page.text.includes('Check flights') && page.text.includes('checkFlights') && !page.text.includes('verifyAllRoutes('));
  check('current provider copy is present', page.text.includes('SerpApi') && !page.text.includes('Amadeus sandbox'));

} catch (error) {
  check('site is reachable', false, error.message);
}

const failed = checks.filter(checkResult => !checkResult.passed).length;
console.log(`\n${failed ? `${failed} check(s) failed` : 'All smoke checks passed'} for ${baseUrl}`);
process.exitCode = failed ? 1 : 0;
