import { zhCN } from './zh-CN'
import { en } from './en'

type Lang = 'zh-CN' | 'en'

const messages: Record<Lang, Record<string, string>> = {
  'zh-CN': zhCN,
  'en': en,
}

/** 从 AppStore 获取当前语言，然后翻译 key */
export function t(key: string, locale: Lang = 'zh-CN'): string {
  const m = messages[locale]
  return m?.[key] ?? key
}

export type { Lang }
