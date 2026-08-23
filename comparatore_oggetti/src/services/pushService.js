function base64UrlToUint8Array(base64Url) {
  const padding = '='.repeat((4 - (base64Url.length % 4)) % 4)
  const base64 = (base64Url + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  return Uint8Array.from([...raw].map(char => char.charCodeAt(0)))
}

export function notifichePushSupportate() {
  return 'serviceWorker' in navigator && 'PushManager' in window
}

export async function statoSottoscrizionePush() {
  if (!notifichePushSupportate()) return false
  const registration = await navigator.serviceWorker.ready
  const subscription = await registration.pushManager.getSubscription()
  return Boolean(subscription)
}

export async function attivaNotifichePush() {
  if (!notifichePushSupportate()) {
    throw new Error('Le notifiche push non sono supportate su questo browser/dispositivo')
  }

  const permesso = await Notification.requestPermission()
  if (permesso !== 'granted') {
    throw new Error('Permesso per le notifiche negato')
  }

  const risposta = await fetch('/api/push/public-key')
  if (!risposta.ok) {
    throw new Error('Notifiche push non configurate sul server')
  }
  const { chiavePubblica } = await risposta.json()

  const registration = await navigator.serviceWorker.ready
  let subscription = await registration.pushManager.getSubscription()
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: base64UrlToUint8Array(chiavePubblica)
    })
  }

  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription)
  })

  return subscription
}

export async function disattivaNotifichePush() {
  if (!notifichePushSupportate()) return
  const registration = await navigator.serviceWorker.ready
  const subscription = await registration.pushManager.getSubscription()
  if (!subscription) return

  await fetch('/api/push/unsubscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ endpoint: subscription.endpoint })
  })
  await subscription.unsubscribe()
}
