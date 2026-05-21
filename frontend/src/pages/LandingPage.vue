<template>
  <div class="min-h-screen bg-white dark:bg-slate-900">
    <!-- ── Navbar ── -->
    <nav class="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-gray-100 dark:border-slate-800">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-2.5 group">
            <div class="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center shadow-sm transition-transform group-hover:scale-105">
              <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              </svg>
            </div>
            <span class="text-lg font-bold text-gray-900 dark:text-white">AI 旅行攻略</span>
          </router-link>

          <!-- Nav Links - Desktop -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">功能介绍</a>
            <a href="#how-it-works" class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">使用步骤</a>
            <a href="#faq" class="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">常见问题</a>
          </div>

          <!-- Auth Buttons -->
          <div class="flex items-center gap-3">
            <router-link
              to="/login"
              class="hidden sm:inline-flex px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
            >
              登录
            </router-link>
            <router-link
              to="/register"
              class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-xl shadow-sm shadow-primary-200 dark:shadow-primary-900/30 hover:shadow-md transition-all duration-200"
            >
              免费注册
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- ── Hero ── -->
    <section class="relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-20 left-1/4 w-72 h-72 bg-primary-100 dark:bg-primary-900/20 rounded-full blur-3xl opacity-40"></div>
        <div class="absolute bottom-20 right-1/4 w-96 h-96 bg-primary-50 dark:bg-primary-900/10 rounded-full blur-3xl opacity-30"></div>
      </div>

      <div class="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 sm:pt-28 sm:pb-32">
        <div class="text-center max-w-3xl mx-auto">
          <!-- 标签 -->
          <div class="inline-flex items-center gap-1.5 px-3 py-1 bg-brand-50 dark:bg-brand-900/30 border border-brand-200 dark:border-brand-800 rounded-full text-xs font-medium text-brand-700 dark:text-brand-300 mb-6">
            <span class="w-1.5 h-1.5 bg-brand-500 rounded-full animate-pulse"></span>
            AI 驱动的智能旅行规划
          </div>

          <!-- 标题 -->
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 dark:text-white leading-tight tracking-tight">
            <span class="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">AI 智能</span>
            旅行攻略生成
          </h1>

          <!-- 副标题 -->
          <p class="mt-6 text-lg sm:text-xl text-gray-500 dark:text-gray-400 leading-relaxed max-w-2xl mx-auto">
            输入目的地，用自然语言描述你的旅行偏好，<br class="hidden sm:block" />
            AI 自动规划行程、生成复古民国风格旅行海报，让每一次旅行都有专属记忆。
          </p>

          <!-- CTA 按钮 -->
          <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <router-link
              to="/register"
              class="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white text-base font-semibold rounded-xl shadow-lg shadow-primary-200 dark:shadow-primary-900/30 hover:-translate-y-0.5 hover:shadow-2xl transition-all duration-200 flex items-center justify-center gap-2"
            >
              立即开始规划
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </router-link>
            <a
              href="#features"
              class="w-full sm:w-auto px-8 py-3.5 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-gray-300 text-base font-semibold rounded-xl hover:bg-gray-50 dark:hover:bg-slate-700 hover:shadow-md transition-all duration-200 flex items-center justify-center gap-2"
            >
              了解功能
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
              </svg>
            </a>
          </div>

          <!-- Hero 插画区 -->
          <div class="mt-16 relative">
            <div class="bg-gradient-to-b from-gray-50 to-white dark:from-slate-800 dark:to-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 shadow-xl p-6 sm:p-8">
              <div class="aspect-[16/9] bg-gradient-to-br from-amber-50 to-brand-50 dark:from-slate-700 dark:to-slate-800 rounded-xl flex items-center justify-center">
                <div class="text-center px-6">
                  <div class="w-16 h-16 mx-auto mb-4 bg-brand-100 dark:bg-brand-900/30 rounded-2xl flex items-center justify-center">
                    <svg class="w-8 h-8 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    </svg>
                  </div>
                  <p class="text-gray-400 dark:text-gray-500 text-sm font-medium">输入你的目的地</p>
                  <p class="text-gray-300 dark:text-gray-600 text-xs mt-1">AI 将为你规划行程并生成复古海报</p>
                </div>
              </div>
            </div>
            <!-- 浮动标签 1 -->
            <div class="absolute -top-3 -right-3 sm:-top-4 sm:-right-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-100 dark:border-slate-700 px-3 py-2 animate-slide-in hidden sm:block">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 bg-brand-400 rounded-full"></span>
                <span class="text-xs font-medium text-gray-700 dark:text-gray-300">攻略生成完成</span>
              </div>
            </div>
            <!-- 浮动标签 2 -->
            <div class="absolute -bottom-3 -left-3 sm:-bottom-4 sm:-left-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-100 dark:border-slate-700 px-3 py-2 animate-slide-in hidden sm:block" style="animation-delay: 0.3s">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="text-xs font-medium text-gray-700 dark:text-gray-300">海报已生成</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 功能介绍 ── -->
    <section id="features" class="py-20 sm:py-28 bg-gray-50 dark:bg-slate-800/50">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">智能旅行规划</h2>
          <p class="mt-4 text-lg text-gray-500 dark:text-gray-400">三步获取你的专属旅行攻略</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- 功能 1 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-gray-100 dark:border-slate-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div class="w-14 h-14 bg-gradient-to-br from-brand-100 to-brand-50 dark:from-brand-900/30 dark:to-brand-800/20 rounded-xl flex items-center justify-center mb-5">
              <svg class="w-7 h-7 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">智能行程规划</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
              输入目的地和天数，AI 自动规划每日详细行程，涵盖景点、美食、住宿、预算等，像专业旅行规划师一样为你量身定制。
            </p>
          </div>

          <!-- 功能 2 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-gray-100 dark:border-slate-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div class="w-14 h-14 bg-gradient-to-br from-amber-100 to-amber-50 dark:from-amber-900/30 dark:to-amber-800/20 rounded-xl flex items-center justify-center mb-5">
              <svg class="w-7 h-7 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5z"/>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">复古海报生成</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
              每次旅行攻略生成后，AI 自动绘制一张民国老报纸风格的复古海报，泛黄纸纹、竖排排版、手绘插画，让旅行记忆更有温度。
            </p>
          </div>

          <!-- 功能 3 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-gray-100 dark:border-slate-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
            <div class="w-14 h-14 bg-gradient-to-br from-brand-100 to-brand-50 dark:from-brand-900/30 dark:to-brand-800/20 rounded-xl flex items-center justify-center mb-5">
              <svg class="w-7 h-7 text-brand-600 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">自由对话交互</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
              直接用中文输入目的地和偏好，AI 理解你的需求。支持自由对话优化行程，就像和一个资深旅行规划师聊天一样自然。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── 使用步骤 ── -->
    <section id="how-it-works" class="py-20 sm:py-28">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">三步获取旅行攻略</h2>
          <p class="mt-4 text-lg text-gray-500 dark:text-gray-400">简单三步，获得你的专属旅行规划</p>
        </div>

        <div class="grid md:grid-cols-3 gap-12 relative">
          <!-- 连接线（桌面端） -->
          <div class="hidden md:block absolute top-16 left-[calc(16.67%+2rem)] right-[calc(16.67%+2rem)] h-0.5 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200 dark:from-primary-800 dark:via-primary-600 dark:to-primary-800"></div>

          <!-- 步骤 1 -->
          <div class="text-center relative">
            <div class="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-lg shadow-primary-200 dark:shadow-primary-900/30 flex items-center justify-center relative z-10">
              <span class="text-2xl font-bold text-white">1</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">输入目的地</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed max-w-xs mx-auto">
              输入你想去的城市和天数，如"杭州3日游"，AI 自动解析你的旅行需求
            </p>
          </div>

          <!-- 步骤 2 -->
          <div class="text-center relative">
            <div class="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-lg shadow-primary-200 dark:shadow-primary-900/30 flex items-center justify-center relative z-10">
              <span class="text-2xl font-bold text-white">2</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">AI 规划行程</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed max-w-xs mx-auto">
              AI 自动生成每日详细行程，涵盖景点、美食、住宿、预算等，还可以根据偏好定制
            </p>
          </div>

          <!-- 步骤 3 -->
          <div class="text-center relative">
            <div class="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-lg shadow-primary-200 dark:shadow-primary-900/30 flex items-center justify-center relative z-10">
              <span class="text-2xl font-bold text-white">3</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">获取攻略海报</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed max-w-xs mx-auto">
              AI 生成完整攻略并绘制民国复古风格旅行海报，可随时查看和下载
            </p>
          </div>
        </div>

        <!-- 底部 CTA -->
        <div class="text-center mt-16">
          <router-link
            to="/register"
            class="inline-flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white text-base font-semibold rounded-xl shadow-lg shadow-primary-200 dark:shadow-primary-900/30 hover:-translate-y-0.5 hover:shadow-2xl transition-all duration-200"
          >
            立即开始规划
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
            </svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── 常见问题 ── -->
    <section id="faq" class="py-20 sm:py-28 bg-gray-50 dark:bg-slate-800/50">
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">常见问题</h2>
          <p class="mt-4 text-lg text-gray-500 dark:text-gray-400">快速了解 AI 旅行攻略</p>
        </div>

        <div class="space-y-4">
          <!-- Q1 -->
          <details class="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-200">
            <summary class="flex items-center justify-between cursor-pointer py-4 px-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
              <span class="text-gray-800 dark:text-gray-200 font-medium">AI 旅行攻略支持哪些目的地？</span>
              <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </summary>
            <div class="px-6 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed border-t border-gray-100 dark:border-slate-700 pt-3">
              支持国内外任意旅游城市和景点。无论是国内的杭州、成都、大理，还是国外的东京、巴黎、曼谷，AI 都能为你生成详细的旅行攻略。
            </div>
          </details>

          <!-- Q2 -->
          <details class="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-200">
            <summary class="flex items-center justify-between cursor-pointer py-4 px-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
              <span class="text-gray-800 dark:text-gray-200 font-medium">生成攻略需要多长时间？</span>
              <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </summary>
            <div class="px-6 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed border-t border-gray-100 dark:border-slate-700 pt-3">
              通常需要 30-90 秒，具体取决于目的地复杂度和 AI 模型响应速度。攻略文本会流式实时显示，你可以边看边等海报生成。
            </div>
          </details>

          <!-- Q3 -->
          <details class="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-200">
            <summary class="flex items-center justify-between cursor-pointer py-4 px-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
              <span class="text-gray-800 dark:text-gray-200 font-medium">生成的攻略可以保存吗？</span>
              <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </summary>
            <div class="px-6 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed border-t border-gray-100 dark:border-slate-700 pt-3">
              所有对话记录都会自动保存在历史记录中，方便随时查看。生成的复古风格海报也可以直接下载保存到本地。
            </div>
          </details>

          <!-- Q4 -->
          <details class="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-200">
            <summary class="flex items-center justify-between cursor-pointer py-4 px-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
              <span class="text-gray-800 dark:text-gray-200 font-medium">可以在手机上使用吗？</span>
              <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </summary>
            <div class="px-6 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed border-t border-gray-100 dark:border-slate-700 pt-3">
              支持。我们采用了响应式设计，在手机和平板等移动设备上也能正常使用所有功能，随时随地规划旅行。
            </div>
          </details>

          <!-- Q5 -->
          <details class="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-200">
            <summary class="flex items-center justify-between cursor-pointer py-4 px-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
              <span class="text-gray-800 dark:text-gray-200 font-medium">海报是什么风格的？</span>
              <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </summary>
            <div class="px-6 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed border-t border-gray-100 dark:border-slate-700 pt-3">
              海报采用民国复古老报纸风格设计，泛黄牛皮纸底色、竖排排版、手绘水墨风景插画，充满怀旧年代氛围。每张海报都是独一无二的旅行纪念。
            </div>
          </details>
        </div>
      </div>
    </section>

    <!-- ── Footer ── -->
    <footer class="border-t border-gray-100 dark:border-slate-800 bg-gray-50 dark:bg-slate-900">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              </svg>
            </div>
            <span class="text-sm font-semibold text-gray-800 dark:text-white">AI 旅行攻略</span>
          </div>
          <p class="text-sm text-gray-400 dark:text-gray-500">© 2024 AI 旅行攻略 · 智能旅行规划</p>
          <div class="flex items-center gap-6">
            <a href="#faq" class="text-sm text-gray-400 dark:text-gray-500 hover:text-brand-500 transition-colors">常见问题</a>
            <router-link to="/login" class="text-sm text-gray-400 dark:text-gray-500 hover:text-brand-500 transition-colors">登录</router-link>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Landing page - no auth required
</script>
