/**
 * 图片下载 composable
 * 从图片 URL 下载图片到本地
 */
export function downloadImage(url: string, filename?: string) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename || url.split('/').pop() || 'image.png'
  // 跨域图片需要 fetch + blob
  if (url.startsWith('http')) {
    fetch(url, { mode: 'cors' })
      .then(res => res.blob())
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob)
        link.href = blobUrl
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(blobUrl)
      })
      .catch(() => {
        // fallback: 直接打开链接
        window.open(url, '_blank')
      })
  } else {
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}
