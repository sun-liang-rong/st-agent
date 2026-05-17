<template>
  <div class="h-full bg-gray-50 dark:bg-slate-900 overflow-y-auto p-6">
    <div class="max-w-3xl mx-auto">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">帮助</h1>
      
      <div class="space-y-8">
        <!-- 使用步骤 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">如何使用</h2>
          
          <div class="space-y-4">
            <div class="flex gap-4">
              <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                <span class="text-primary-600 dark:text-primary-400 font-bold">1</span>
              </div>
              <div>
                <h3 class="font-medium text-gray-800 dark:text-white mb-1">上传文件</h3>
                <p class="text-gray-600 dark:text-gray-400">点击上传区域或拖拽 Excel 文件（支持 .xlsx, .xls, .csv 格式）</p>
              </div>
            </div>
            
            <div class="flex gap-4">
              <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                <span class="text-primary-600 dark:text-primary-400 font-bold">2</span>
              </div>
              <div>
                <h3 class="font-medium text-gray-800 dark:text-white mb-1">输入需求</h3>
                <p class="text-gray-600 dark:text-gray-400">描述你想要分析的数据和生成的报表类型</p>
              </div>
            </div>
            
            <div class="flex gap-4">
              <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                <span class="text-primary-600 dark:text-primary-400 font-bold">3</span>
              </div>
              <div>
                <h3 class="font-medium text-gray-800 dark:text-white mb-1">生成报表</h3>
                <p class="text-gray-600 dark:text-gray-400">点击发送，AI 将自动分析数据并生成可视化报表</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 常见问题 -->
        <div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">常见问题</h2>
          
          <div class="space-y-4">
            <details class="group">
              <summary class="flex items-center justify-between cursor-pointer py-3 px-4 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700">
                <span class="text-gray-700 dark:text-gray-300 font-medium">支持哪些文件格式？</span>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </summary>
              <div class="pt-2 pb-4 px-4 text-gray-600 dark:text-gray-400">
                支持 .xlsx, .xls, .csv 格式的 Excel 文件。文件大小不超过 10MB。
              </div>
            </details>
            
            <details class="group">
              <summary class="flex items-center justify-between cursor-pointer py-3 px-4 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700">
                <span class="text-gray-700 dark:text-gray-300 font-medium">生成报表需要多长时间？</span>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </summary>
              <div class="pt-2 pb-4 px-4 text-gray-600 dark:text-gray-400">
                通常需要 30-60 秒，具体取决于数据量和 AI 模型响应速度。
              </div>
            </details>
            
            <details class="group">
              <summary class="flex items-center justify-between cursor-pointer py-3 px-4 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700">
                <span class="text-gray-700 dark:text-gray-300 font-medium">数据安全吗？</span>
                <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </summary>
              <div class="pt-2 pb-4 px-4 text-gray-600 dark:text-gray-400">
                你的数据只发送到 AI 模型用于分析和生成报表，不会被存储或用于其他用途。
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
