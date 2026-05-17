export const en: Record<string, string> = {
  // Navigation
  'nav.home': 'Home',
  'nav.history': 'History',
  'nav.settings': 'Settings',
  'nav.help': 'Help',

  // Sidebar
  'app.title': 'AI Report',
  'app.subtitle': 'Smart Data Analysis',
  'sidebar.theme': 'Theme',
  'sidebar.dark': 'Dark',
  'sidebar.light': 'Light',
  'sidebar.logout': 'Logout',

  // Login
  'login.title': 'Welcome Back',
  'login.subtitle': 'Sign in to AI Report Platform',
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
  'register.subtitle': 'Register for AI Report Platform',
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
  'home.emptyTitle': 'AI Assistant',
  'home.emptyDesc': 'Ask me anything, or upload an Excel file for data analysis and report generation',
  'home.uploadArea': 'Upload Excel file to generate report',
  'home.uploadHint': 'Supports .xlsx, .xls, .csv',
  'home.inputPlaceholder': 'Type a message, or upload an Excel file...',
  'home.inputPlaceholderFile': 'Enter your analysis requirement...',
  'home.send': 'Send',
  'home.generating': 'Generating...',
  'home.thinking': 'Thinking...',
  'home.download': 'Download Image',
  'home.uploadFailed': 'Upload failed, please try again',
  'home.generateFailed': 'Report generation failed, please try again',
  'home.chatFailed': 'Chat service temporarily unavailable',

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

  'settings.apiConfig': 'API Configuration',
  'settings.apiKey': 'API Key',
  'settings.modelSettings': 'Model Settings',
  'settings.promptModel': 'Prompt Model',
  'settings.imageModel': 'Image Model',
  'settings.save': 'Save Settings',
  'settings.saved': 'Settings saved!',
}

export type TranslationKeys = keyof typeof en
