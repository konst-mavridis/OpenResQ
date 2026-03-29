// This script runs synchronously before React hydration to prevent theme flash
export function getThemeScript(): string {
  return `(function() {
    try {
      const theme = localStorage.getItem('theme') || 'system';
      const isSystemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = theme === 'dark' || (theme === 'system' && isSystemDark);
      
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (e) {
      // Fallback to default theme
      document.documentElement.classList.add('dark');
    }
  })();`;
}
