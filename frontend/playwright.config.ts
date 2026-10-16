import { defineConfig } from '@playwright/test';

const python = process.env['E2E_PYTHON'];
if (!python || !process.env['E2E_SCHEMA']) throw new Error('Run scripts/verify.py to prepare the isolated database.');
const browser = process.env['E2E_BROWSER'] || 'chromium';
export default defineConfig({
  testDir: './e2e',
  workers: 1,
  fullyParallel: false,
  timeout: 45000,
  use: {
    baseURL: 'http://127.0.0.1:4202',
    browserName: 'chromium',
    channel: browser === 'chromium' ? undefined : browser,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: [
    { command: `"${python}" ../backend/tests/e2e_server.py`, url: 'http://127.0.0.1:5002/api/health', reuseExistingServer: false, timeout: 60000 },
    { command: 'npx ng serve --host 127.0.0.1 --port 4202 --proxy-config e2e/proxy.cjs', url: 'http://127.0.0.1:4202', reuseExistingServer: false, timeout: 120000 },
  ],
});
