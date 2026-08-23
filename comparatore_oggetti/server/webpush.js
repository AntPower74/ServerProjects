import webpush from 'web-push'

const { VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT } = process.env

const abilitato = Boolean(VAPID_PUBLIC_KEY && VAPID_PRIVATE_KEY)

if (abilitato) {
  webpush.setVapidDetails(VAPID_SUBJECT || 'mailto:admin@example.com', VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY)
} else {
  console.warn('VAPID_PUBLIC_KEY/VAPID_PRIVATE_KEY mancanti: le notifiche push sono disabilitate.')
}

export const pushAbilitato = abilitato
export default webpush
