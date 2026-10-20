export const isMyHanhSite = (location = globalThis.location) => Boolean(
  location && (location.hostname.includes('myhanh') || new URLSearchParams(location.search).get('mode') === 'myhanh')
)

export const ELEMENTARY_GRADE = 'Elementary (Grades 1 - 5)'
export const isElementaryGrade = (grade) => grade === ELEMENTARY_GRADE || grade === 'primary'

export const mediaUrl = (url, backendUrl = '') => {
  if (!url) return ''
  if (/^(https?:|data:|blob:)/i.test(url)) return url
  return `${backendUrl.replace(/\/$/, '')}/${url.replace(/^\//, '')}`
}
