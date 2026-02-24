import type { LucideIcon } from "lucide-react";

/**
 * 【翻译资源结构定义】
 *
 * 约定：每种语言（Locale）都需要提供一份满足该接口的翻译对象，
 * 以保证 UI 文案在不同语言下的字段一致性与类型安全。
 */
export interface Translations {
  // Locale meta
  /**
   * 【语言元信息】
   */
  locale: {
    /**
     * 【本地化名称】
     * 例如：中文环境显示“简体中文”，英文环境显示“English”。
     */
    localName: string;
  };

  // Common
  /**
   * 【通用文案】
   */
  common: {
    home: string;
    settings: string;
    delete: string;
    rename: string;
    share: string;
    openInNewWindow: string;
    close: string;
    more: string;
    search: string;
    download: string;
    thinking: string;
    artifacts: string;
    public: string;
    custom: string;
    notAvailableInDemoMode: string;
    loading: string;
    version: string;
    lastUpdated: string;
    code: string;
    preview: string;
    cancel: string;
    save: string;
    install: string;
    create: string;
  };

  // Welcome
  /**
   * 【欢迎页相关文案】
   */
  welcome: {
    greeting: string;
    description: string;
    createYourOwnSkill: string;
    createYourOwnSkillDescription: string;
  };

  // Clipboard
  /**
   * 【剪贴板相关文案】
   */
  clipboard: {
    copyToClipboard: string;
    copiedToClipboard: string;
    failedToCopyToClipboard: string;
    linkCopied: string;
  };

  // Input Box
  /**
   * 【输入框相关文案】
   */
  inputBox: {
    placeholder: string;
    createSkillPrompt: string;
    addAttachments: string;
    mode: string;
    flashMode: string;
    flashModeDescription: string;
    reasoningMode: string;
    reasoningModeDescription: string;
    proMode: string;
    proModeDescription: string;
    ultraMode: string;
    ultraModeDescription: string;
    searchModels: string;
    surpriseMe: string;
    surpriseMePrompt: string;
    suggestions: {
      suggestion: string;
      prompt: string;
      /**
       * 【建议项图标】
       * 使用 lucide-react 的图标组件类型。
       */
      icon: LucideIcon;
    }[];
    /**
     * 【创建建议列表】
     *
     * 该数组允许两种元素：
     * - 普通建议项：包含 suggestion/prompt/icon
     * - 分隔符：{ type: "separator" }
     */
    suggestionsCreate: (
      | {
          suggestion: string;
          prompt: string;
          icon: LucideIcon;
        }
      | {
          type: "separator";
        }
    )[];
  };

  // Sidebar
  /**
   * 【侧边栏相关文案】
   */
  sidebar: {
    recentChats: string;
    newChat: string;
    chats: string;
    demoChats: string;
  };

  // Breadcrumb
  /**
   * 【面包屑导航文案】
   */
  breadcrumb: {
    workspace: string;
    chats: string;
  };

  // Workspace
  /**
   * 【工作区顶部/菜单相关文案】
   */
  workspace: {
    officialWebsite: string;
    githubTooltip: string;
    settingsAndMore: string;
    visitGithub: string;
    reportIssue: string;
    contactUs: string;
    about: string;
  };

  // Conversation
  /**
   * 【会话区（消息列表）文案】
   */
  conversation: {
    noMessages: string;
    startConversation: string;
  };

  // Chats
  /**
   * 【聊天列表文案】
   */
  chats: {
    searchChats: string;
  };

  // Page titles (document title)
  /**
   * 【页面标题（document.title）文案】
   */
  pages: {
    appName: string;
    chats: string;
    newChat: string;
    untitled: string;
  };

  // Tool calls
  /**
   * 【工具调用相关文案】
   */
  toolCalls: {
    /**
     * 【更多步骤提示】
     * @param count - 【剩余步骤数】
     * @returns 【提示文案】
     */
    moreSteps: (count: number) => string;
    lessSteps: string;
    executeCommand: string;
    presentFiles: string;
    needYourHelp: string;
    /**
     * 【使用某工具】
     * @param toolName - 【工具名称】
     * @returns 【提示文案】
     */
    useTool: (toolName: string) => string;
    searchForRelatedInfo: string;
    searchForRelatedImages: string;
    /**
     * 【搜索提示】
     * @param query - 【搜索关键词】
     * @returns 【提示文案】
     */
    searchFor: (query: string) => string;
    /**
     * 【搜索相关图片提示】
     * @param query - 【搜索关键词】
     * @returns 【提示文案】
     */
    searchForRelatedImagesFor: (query: string) => string;
    /**
     * 【在 Web 上搜索提示】
     * @param query - 【搜索关键词】
     * @returns 【提示文案】
     */
    searchOnWebFor: (query: string) => string;
    viewWebPage: string;
    listFolder: string;
    readFile: string;
    writeFile: string;
    clickToViewContent: string;
    writeTodos: string;
    skillInstallTooltip: string;
  };

  // Subtasks
  /**
   * 【子任务状态文案】
   */
  subtasks: {
    subtask: string;
    /**
     * 【执行中提示】
     * @param count - 【执行中的数量】
     * @returns 【提示文案】
     */
    executing: (count: number) => string;
    in_progress: string;
    completed: string;
    failed: string;
  };

  // Settings
  /**
   * 【设置页文案】
   */
  settings: {
    title: string;
    description: string;
    sections: {
      appearance: string;
      memory: string;
      tools: string;
      skills: string;
      notification: string;
      about: string;
    };
    memory: {
      title: string;
      description: string;
      empty: string;
      rawJson: string;
      markdown: {
        overview: string;
        userContext: string;
        work: string;
        personal: string;
        topOfMind: string;
        historyBackground: string;
        recentMonths: string;
        earlierContext: string;
        longTermBackground: string;
        updatedAt: string;
        facts: string;
        empty: string;
        table: {
          category: string;
          confidence: string;
          confidenceLevel: {
            veryHigh: string;
            high: string;
            normal: string;
            unknown: string;
          };
          content: string;
          source: string;
          createdAt: string;
          view: string;
        };
      };
    };
    appearance: {
      themeTitle: string;
      themeDescription: string;
      system: string;
      light: string;
      dark: string;
      systemDescription: string;
      lightDescription: string;
      darkDescription: string;
      languageTitle: string;
      languageDescription: string;
    };
    tools: {
      title: string;
      description: string;
    };
    skills: {
      title: string;
      description: string;
      createSkill: string;
      emptyTitle: string;
      emptyDescription: string;
      emptyButton: string;
    };
    notification: {
      title: string;
      description: string;
      requestPermission: string;
      deniedHint: string;
      testButton: string;
      testTitle: string;
      testBody: string;
      notSupported: string;
      disableNotification: string;
    };
    acknowledge: {
      emptyTitle: string;
      emptyDescription: string;
    };
  };
}
