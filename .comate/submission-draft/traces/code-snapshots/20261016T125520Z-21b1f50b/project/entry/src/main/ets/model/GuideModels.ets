export interface GuideStep {
  id: string;
  stepNo: number;
  icon: string;
  title: string;
  description: string;
  detail: string;
  category: GuideCategory;
}

export type GuideCategory = 'learning' | 'wordbook' | 'text' | 'settings' | 'general';

export interface GuideCategoryInfo {
  id: GuideCategory;
  name: string;
  icon: string;
  color: string;
}

export const GUIDE_CATEGORIES: GuideCategoryInfo[] = [
  { id: 'learning', name: '学习功能', icon: '📚', color: '#007DFF' },
  { id: 'wordbook', name: '词书管理', icon: '📖', color: '#4CAF50' },
  { id: 'text', name: '文本库', icon: '📝', color: '#FF9800' },
  { id: 'settings', name: '设置', icon: '⚙️', color: '#9C27B0' },
  { id: 'general', name: '基础操作', icon: '🏠', color: '#607D8B' }
];

export interface HelpArticle {
  id: string;
  title: string;
  content: string;
  category: HelpCategory;
  tags: string[];
  relatedArticles: string[];
}

export type HelpCategory = 'getting_started' | 'learning' | 'wordbook' | 'text_library' | 'sync' | 'settings' | 'faq';

export interface HelpCategoryInfo {
  id: HelpCategory;
  name: string;
  icon: string;
  description: string;
}

export const HELP_CATEGORIES: HelpCategoryInfo[] = [
  { id: 'getting_started', name: '快速入门', icon: '🚀', description: '新手必看，快速上手指南' },
  { id: 'learning', name: '学习功能', icon: '📚', description: '学习页面、复习机制、记忆算法' },
  { id: 'wordbook', name: '词书管理', icon: '📖', description: '词书选择、导入、进度管理' },
  { id: 'text_library', name: '文本库', icon: '📝', description: '导入文章、阅读查词' },
  { id: 'sync', name: '数据同步', icon: '☁️', description: 'WebDAV同步、备份恢复' },
  { id: 'settings', name: '设置', icon: '⚙️', description: 'API配置、偏好设置' },
  { id: 'faq', name: '常见问题', icon: '❓', description: '问题解答与故障排除' }
];

export interface OnboardingState {
  hasSeenOnboarding: boolean;
  completedSteps: string[];
  skippedAt: number | null;
  completedAt: number | null;
}
