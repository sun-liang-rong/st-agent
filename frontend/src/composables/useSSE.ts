/**
 * SSE 流式解析 composable
 * 统一处理 ReadableStream 的 SSE 解析逻辑
 */

export interface SSEHandlers {
  onToken?: (data: any) => void
  onDone?: (data: any) => void
  onError?: (data: any) => void
  onImageIntent?: (data: any) => void
  onImageProgress?: (data: any) => void
  onImageResult?: (data: any) => void
}

export function useSSE() {
  /**
   * 从 fetch Response 中读取 SSE 流
   */
  async function readSSE(response: Response, handlers: SSEHandlers) {
    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            switch (currentEvent) {
              case 'token':
                handlers.onToken?.(data)
                break
              case 'done':
                handlers.onDone?.(data)
                break
              case 'error':
                handlers.onError?.(data)
                break
              case 'image_intent':
                handlers.onImageIntent?.(data)
                break
              case 'image_progress':
                handlers.onImageProgress?.(data)
                break
              case 'image_result':
                handlers.onImageResult?.(data)
                break
            }
          } catch { /* ignore non-JSON data lines */ }
        }
      }
    }
  }

  return { readSSE }
}
