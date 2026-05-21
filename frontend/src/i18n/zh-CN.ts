export const zhCN: Record<string, string> = {
  // 导航
  'nav.home': '旅行攻略',
  'nav.history': '历史记录',
  'nav.settings': '设置',
  'nav.help': '帮助',

  // 侧边栏
  'app.title': 'AI 旅行攻略',
  'app.subtitle': '智能旅行规划助手',
  'sidebar.theme': '切换主题',
  'sidebar.dark': '深色',
  'sidebar.light': '浅色',
  'sidebar.logout': '退出登录',

  // 登录注册
  'login.title': '欢迎回来',
  'login.subtitle': '登录到 AI 旅行攻略平台',
  'login.username': '用户名',
  'login.password': '密码',
  'login.remember': '记住我',
  'login.submit': '登录',
  'login.loading': '登录中...',
  'login.noAccount': '还没有账户？',
  'login.register': '立即注册',
  'login.error': '用户名或密码错误',

  'register.title': '创建账户',
  'register.subtitle': '注册 AI 旅行攻略平台账号',
  'register.username': '用户名',
  'register.password': '密码',
  'register.confirmPassword': '确认密码',
  'register.submit': '创建账户',
  'register.loading': '注册中...',
  'register.hasAccount': '已有账户？',
  'register.login': '立即登录',
  'register.success': '注册成功！正在跳转...',
  'register.passwordMismatch': '两次输入的密码不一致',

  // 首页
  'home.emptyTitle': 'AI 旅行规划师',
  'home.emptyDesc': '输入目的地，获取详细的旅行攻略和精美复古海报',
  'home.inputPlaceholder': '输入目的地，如「杭州3日游攻略」',
  'home.send': '发送',
  'home.generating': '规划中...',
  'home.thinking': '思考中...',
  'home.download': '下载海报',
  'home.chatFailed': '服务暂时不可用，请稍后再试',

  // 报表生成
  'report.creating': '正在创建生成任务...',
  'report.progress1': '正在读取文件数据...',
  'report.progress2': '正在分析数据...',
  'report.progress3': '正在生成图表...',
  'report.progress4': '生成完成',
  'report.complete': '已根据你的需求分析完成！',

  // 历史
  'history.title': '历史记录',
  'history.empty': '开始使用后，这里会显示你的所有记录',
  'history.noReports': '上传 Excel 并生成报表后，这里会显示记录',
  'history.noChats': '与 AI 对话后，这里会显示聊天记录',
  'history.interactions': '条互动',
  'history.deleteConfirm': '确定要删除这条会话',
  'history.deleteFailed': '删除失败',

  // 设置
  'settings.title': '设置',
  'settings.appearance': '外观',
  'settings.darkMode': '深色模式',
  'settings.darkModeDesc': '切换深色/浅色主题',
  'settings.language': '语言',
  'settings.languageDesc': '切换界面显示语言',
  'settings.langZh': '中文',
  'settings.langEn': 'English',

  'settings.font': '字体',
  'settings.fontSize': '字体大小',
  'settings.fontSizeDesc': '调整界面文字大小',
  'settings.fontSmall': '小',
  'settings.fontMedium': '中',
  'settings.fontLarge': '大',
  'settings.codeFont': '代码字体',
  'settings.codeFontDesc': '代码块使用的等宽字体',
  'settings.codeFontMono': '等宽字体',
  'settings.codeFontSystem': '系统字体',
  'settings.density': '消息密度',
  'settings.densityDesc': '控制消息列表的间距',
  'settings.densityComfortable': '宽松',
  'settings.densityCompact': '紧凑',

  // 设置 - 旧模块（即将去掉）
  'settings.apiConfig': 'API 配置',
  'settings.apiKey': '商汤 API Key',
  'settings.modelSettings': '模型设置',
  'settings.promptModel': '提示词生成模型',
  'settings.imageModel': '图片生成模型',
  'settings.save': '保存设置',
  'settings.saved': '设置已保存！',
}

export type TranslationKeys = keyof typeof zhCN
