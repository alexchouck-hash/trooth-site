export function p(targetPath: string): string {
  const rawBase = import.meta.env.BASE_URL || '/';
  const base = rawBase.replace(/\/$/, '');
  if (!targetPath || targetPath === '/') {
    return base ? `${base}/` : '/';
  }
  const clean = targetPath.startsWith('/') ? targetPath : `/${targetPath}`;
  return `${base}${clean}`;
}
