export function getTelegramWebApp() {
  return window.Telegram?.WebApp || null
}

export function isTelegramMiniApp() {
  const webApp = getTelegramWebApp()
  if (!webApp) return false

  const hasInitData = Boolean(webApp.initData)
  const hasTelegramUser = Boolean(webApp.initDataUnsafe?.user)
  const platform = typeof webApp.platform === 'string' ? webApp.platform : ''
  const hasKnownPlatform = Boolean(platform && platform !== 'unknown')

  return hasInitData || hasTelegramUser || hasKnownPlatform
}

export function canUseTelegramAuth() {
  return Boolean(getTelegramWebApp()?.initData)
}

export function initTelegramWebApp() {
  const webApp = getTelegramWebApp()
  if (!webApp) return null

  webApp.ready()
  webApp.expand()
  return webApp
}
