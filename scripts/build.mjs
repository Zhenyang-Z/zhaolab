// npm entry point for hosts such as Cloudflare Pages. No npm dependencies.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const cwd = fileURLToPath(new URL('../', import.meta.url));
const python = process.platform === 'win32' ? 'python' : 'python3';
const scripts = process.argv.includes('--check')
  ? ['scripts/check.py']
  : ['scripts/build.py', 'scripts/check.py'];
for (const script of scripts) {
  const result = spawnSync(python, [script], { cwd, stdio: 'inherit' });
  if (result.error) {
    console.error(`Unable to run ${python}. Install Python 3.10 or newer.`, result.error.message);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}
