export const en: Record<string, string> = {
  // Navigation
  'nav.home': 'Travel Guide',
  'nav.history': 'History',
  'nav.settings': 'Settings',
  'nav.help': 'Help',

  // Sidebar
  'app.title': 'AI Travel Guide',
  'app.subtitle': 'Smart Travel Planner',
  'sidebar.theme': 'Theme',
  'sidebar.dark': 'Dark',
  'sidebar.light': 'Light',
  'sidebar.logout': 'Logout',

  // Login
  'login.title': 'Welcome Back',
  'login.subtitle': 'Sign in to AI Travel Guide',
  'login.username': 'Username',
  'login.password': 'Password',
  'login.remember': 'Remember me',
  'login.submit': 'Sign In',
  'login.loading': 'Signing in...',
  'login.noAccount': "Don't have an account?",
  'login.register': 'Register Now',
  'login.error': 'Invalid username or password',

  // Register
  'register.title': 'Create Account',
  'register.subtitle': 'Register for AI Travel Guide',
  'register.username': 'Username',
  'register.password': 'Password',
  'register.confirmPassword': 'Confirm Password',
  'register.submit': 'Create Account',
  'register.loading': 'Registering...',
  'register.hasAccount': 'Already have an account?',
  'register.login': 'Sign In',
  'register.success': 'Registration successful! Redirecting...',
  'register.passwordMismatch': 'Passwords do not match',

  // Home
  'home.emptyTitle': 'AI Travel Planner',
  'home.emptyDesc': 'Enter a destination to get detailed travel guides and vintage posters',
  'home.inputPlaceholder': 'e.g. "3 days in Hangzhou"',
  'home.send': 'Send',
  'home.generating': 'Planning...',
  'home.thinking': 'Thinking...',
  'home.download': 'Download Poster',
  'home.chatFailed': 'Service temporarily unavailable',

  // Report
  'report.creating': 'Creating generation task...',
  'report.progress1': 'Reading file data...',
  'report.progress2': 'Analyzing data...',
  'report.progress3': 'Generating chart...',
  'report.progress4': 'Complete',
  'report.complete': 'Analysis complete!',

  // History
  'history.title': 'History',
  'history.empty': 'Your activity will appear here',
  'history.noReports': 'No report history yet',
  'history.noChats': 'No chat history yet',
  'history.interactions': 'interactions',
  'history.deleteConfirm': 'Delete this conversation?',
  'history.deleteFailed': 'Delete failed',

  // Settings
  'settings.title': 'Settings',
  'settings.appearance': 'Appearance',
  'settings.darkMode': 'Dark Mode',
  'settings.darkModeDesc': 'Toggle dark/light theme',
  'settings.language': 'Language',
  'settings.languageDesc': 'Change interface language',
  'settings.langZh': '中文',
  'settings.langEn': 'English',
  'settings.font': 'Font',
  'settings.fontSize': 'Font Size',
  'settings.fontSizeDesc': 'Adjust text size across the app',
  'settings.fontSmall': 'Small',
  'settings.fontMedium': 'Medium',
  'settings.fontLarge': 'Large',
  'settings.codeFont': 'Code Font',
  'settings.codeFontDesc': 'Monospace font for code blocks',
  'settings.codeFontMono': 'Monospace',
  'settings.codeFontSystem': 'System Font',
  'settings.density': 'Message Density',
  'settings.densityDesc': 'Control spacing in message lists',
  'settings.densityComfortable': 'Comfortable',
  'settings.densityCompact': 'Compact',

  'settings.apiConfig': 'API Configuration',
  'settings.apiKey': 'API Key',
  'settings.modelSettings': 'Model Settings',
  'settings.promptModel': 'Prompt Model',
  'settings.imageModel': 'Image Model',
  'settings.save': 'Save Settings',
  'settings.saved': 'Settings saved!',
}

export type TranslationKeys = keyof typeof en
