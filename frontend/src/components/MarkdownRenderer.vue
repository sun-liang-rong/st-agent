<template>
  <div class="markdown-body" :class="{ dark: isDark }" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAppStore } from '@/stores/app'

const marked = new Marked({
  gfm: true,
  breaks: true,
})

const appStore = useAppStore()
const isDark = computed(() => appStore.isDark)

const props = defineProps<{
  content: string
}>()

const renderedContent = computed(() => {
  if (!props.content) return ''
  const html = marked.parse(props.content) as string
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'ul', 'ol', 'li',
      'blockquote', 'pre', 'code',
      'strong', 'em', 'del', 'a',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'div', 'span',
      'img',
    ],
    ALLOWED_ATTR: ['href', 'target', 'src', 'alt', 'class'],
  })
})
</script>

<style>
.markdown-body {
  line-height: 1.7;
  word-break: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.3;
}

.markdown-body h1 { font-size: 1.45em; }
.markdown-body h2 { font-size: 1.25em; }
.markdown-body h3 { font-size: 1.1em; }
.markdown-body h4 { font-size: 1.0em; }

.markdown-body p {
  margin-bottom: 0.6em;
}
.markdown-body p:last-child {
  margin-bottom: 0;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 1.5em;
  margin-bottom: 0.6em;
}
.markdown-body li {
  margin-bottom: 0.2em;
}
.markdown-body li > ul,
.markdown-body li > ol {
  margin-bottom: 0;
}

/* ---- code ---- */
.markdown-body code {
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.87em;
  font-family: 'Menlo', 'Consolas', 'Monaco', monospace;
  background: #f1f5f9;
  color: #e11d48;
}
.markdown-body.dark code {
  background: #1e293b;
  color: #f472b6;
}

/* ---- pre ---- */
.markdown-body pre {
  padding: 1em 1.2em;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 0.75em;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}
.markdown-body.dark pre {
  background: #0f172a;
  border-color: #334155;
}
.markdown-body pre code {
  padding: 0;
  background: none;
  color: inherit;
  font-size: 0.84em;
}

/* ---- blockquote ---- */
.markdown-body blockquote {
  padding: 0.5em 1em;
  margin-bottom: 0.75em;
  border-left: 3px solid #94a3b8;
  color: #475569;
  background: #f8fafc;
  border-radius: 0 6px 6px 0;
}
.markdown-body.dark blockquote {
  border-left-color: #64748b;
  color: #94a3b8;
  background: #1e293b;
}

/* ---- table ---- */
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.75em;
  display: block;
  overflow-x: auto;
}
.markdown-body th,
.markdown-body td {
  padding: 0.45em 0.7em;
  border: 1px solid #e2e8f0;
  text-align: left;
}
.markdown-body.dark th,
.markdown-body.dark td {
  border-color: #475569;
}
.markdown-body th {
  font-weight: 600;
  background: #f8fafc;
}
.markdown-body.dark th {
  background: #1e293b;
}
.markdown-body tr:nth-child(even) {
  background: #fafafa;
}
.markdown-body.dark tr:nth-child(even) {
  background: #0f172a;
}

/* ---- link ---- */
.markdown-body a {
  color: #7c3aed;
  text-decoration: underline;
}
.markdown-body a:hover {
  opacity: 0.75;
}

/* ---- hr ---- */
.markdown-body hr {
  margin: 1em 0;
  border: none;
  border-top: 1px solid #e2e8f0;
}
.markdown-body.dark hr {
  border-top-color: #334155;
}

/* ---- img ---- */
.markdown-body img {
  max-width: 100%;
  border-radius: 8px;
  margin: 0.5em 0;
}
</style>
