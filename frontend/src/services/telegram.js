export function getTelegramWebApp() {
  return window.Telegram?.WebApp || null
}

export function hasTelegramWebApp() {
  return Boolean(getTelegramWebApp())
}

export function isTelegramMiniApp() {
  return hasTelegramWebApp()
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
