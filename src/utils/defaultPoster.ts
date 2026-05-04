import posterDEF from '@/assets/posterDEF.jpg'

export function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement | null;

  if (!target) {
    return;
  }

  if (target.dataset.fallbackbackup === 'true') {
    return;
  }

  target.dataset.fallbackbackup = 'true';
  target.src = posterDEF;
}