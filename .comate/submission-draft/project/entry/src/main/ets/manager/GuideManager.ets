import preferences from '@ohos.data.preferences';
import type common from '@ohos.app.ability.common';
import { GuideStep, GuideCategory, OnboardingState } from '../model/GuideModels';

export class GuideManager {
  private static readonly PREFERENCES_NAME: string = 'guide_store';
  private static readonly ONBOARDING_STATE_KEY: string = 'onboarding_state_v2';
  private static instance: GuideManager | null = null;

  private prefs: preferences.Preferences | null = null;
  private context: common.UIAbilityContext | null = null;

  private constructor() {}

  static getInstance(): GuideManager {
    if (GuideManager.instance === null) {
      GuideManager.instance = new GuideManager();
    }
    return GuideManager.instance;
  }

  injectContext(context: common.UIAbilityContext): void {
    this.context = context;
  }

  async initialize(): Promise<boolean> {
    if (this.context === null) {
      return false;
    }
    try {
      this.prefs = await preferences.getPreferences(this.context, GuideManager.PREFERENCES_NAME);
      return true;
    } catch (e) {
      return false;
    }
  }

  async getOnboardingState(): Promise<OnboardingState> {
    if (this.prefs === null) {
      return this.getDefaultState();
    }
    try {
      const json = await this.prefs.get(GuideManager.ONBOARDING_STATE_KEY, '');
      if (typeof json === 'string' && json.length > 0) {
        return JSON.parse(json) as OnboardingState;
      }
    } catch (e) {}
    return this.getDefaultState();
  }

  async setOnboardingSeen(seen: boolean): Promise<void> {
    const state = await this.getOnboardingState();
    state.hasSeenOnboarding = seen;
    if (seen && state.completedAt === null) {
      state.completedAt = Date.now();
    }
    await this.saveState(state);
  }

  async completeStep(stepId: string): Promise<void> {
    const state = await this.getOnboardingState();
    if (!state.completedSteps.includes(stepId)) {
      state.completedSteps.push(stepId);
    }
    await this.saveState(state);
  }

  async skipOnboarding(): Promise<void> {
    const state = await this.getOnboardingState();
    state.skippedAt = Date.now();
    state.hasSeenOnboarding = true;
    await this.saveState(state);
  }

  async completeOnboarding(): Promise<void> {
    const state = await this.getOnboardingState();
    state.hasSeenOnboarding = true;
    state.completedAt = Date.now();
    await this.saveState(state);
  }

  private async saveState(state: OnboardingState): Promise<void> {
    if (this.prefs === null) {
      return;
    }
    try {
      await this.prefs.put(GuideManager.ONBOARDING_STATE_KEY, JSON.stringify(state));
      await this.prefs.flush();
    } catch (e) {}
  }

  private getDefaultState(): OnboardingState {
    return {
      hasSeenOnboarding: false,
      completedSteps: [],
      skippedAt: null,
      completedAt: null
    };
  }

  getGuideSteps(): GuideStep[] {
    return [
      {
        id: 'welcome',
        stepNo: 1,
        icon: '👋',
        title: '欢迎使用 Vignette',
        description: '您的智能英语词汇学习助手',
        detail: 'Vignette 采用 FSRS 记忆算法，结合语境学习，帮助您高效记忆英语单词。让我们开始了解如何使用吧！',
        category: 'general'
      },
      {
        id: 'select_book',
        stepNo: 2,
        icon: '📖',
        title: '选择词书',
        description: '选择适合您的词书开始学习',
        detail: '在首页点击词书卡片，选择 CET4、GRE、高考等内置词书，或导入自定义词书。选择后点击"开始学习"进入今日任务。',
        category: 'wordbook'
      },
      {
        id: 'learning_session',
        stepNo: 3,
        icon: '📚',
        title: '学习任务',
        description: '完成每日学习与复习任务',
        detail: '系统会根据 FSRS 算法安排新词学习和旧词复习。每个单词会展示语境故事，帮助您在场景中理解记忆。',
        category: 'learning'
      },
      {
        id: 'tap_word',
        stepNo: 4,
        icon: '👆',
        title: '点词查义',
        description: '点击单词查看释义和语境',
        detail: '阅读语境时，点击任意单词可查看详细释义、音标、例句。支持收藏到单词本，方便后续复习。',
        category: 'learning'
      },
      {
        id: 'mark_known',
        stepNo: 5,
        icon: '✅',
        title: '标记已知',
        description: '已掌握的单词可减少复习',
        detail: '如果某个单词您已经掌握，可以"标记已知"，系统会减少该单词的复习频率。需要时可在词表或详情页"恢复学习"。',
        category: 'learning'
      },
      {
        id: 'notebook',
        stepNo: 6,
        icon: '⭐',
        title: '单词本收藏',
        description: '收藏重点单词便于复习',
        detail: '收藏功能让您建立个人重点单词清单。收藏的单词会在单词本中显示，方便集中复习和查阅。',
        category: 'learning'
      },
      {
        id: 'text_library',
        stepNo: 7,
        icon: '📝',
        title: '文本库阅读',
        description: '导入文章在阅读中学习',
        detail: '在文本库页面导入 txt 文件或粘贴文章内容，阅读时点击单词查释义并收藏。让学习融入真实阅读场景。',
        category: 'text'
      },
      {
        id: 'settings',
        stepNo: 8,
        icon: '⚙️',
        title: '个性化设置',
        description: '调整学习参数和偏好',
        detail: '在设置页面可以配置每日任务量、学习难度、语境风格、语音朗读等。还可以配置 API 接口和 WebDAV 同步。',
        category: 'settings'
      },
      {
        id: 'sync',
        stepNo: 9,
        icon: '☁️',
        title: '数据同步',
        description: '云端备份学习进度',
        detail: '支持 WebDAV 云同步，可在多设备间同步学习进度和词书数据。定期备份，数据不丢失。',
        category: 'settings'
      },
      {
        id: 'help',
        stepNo: 10,
        icon: '🎉',
        title: '准备就绪',
        description: '开启你的词汇学习之旅',
        detail: '选择词书后点击"开始学习"即可开始。首页"单词本"可查看收藏的单词。祝学习愉快！',
        category: 'general'
      }
    ];
  }

  getStepsByCategory(category: GuideCategory): GuideStep[] {
    return this.getGuideSteps().filter((step: GuideStep) => step.category === category);
  }
}
