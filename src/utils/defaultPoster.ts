import defaultPoster from '@/assets/defaultPoster.webp';
export function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement | null;
  if (!target) {
    return;
  }
  if(target.dataset.fallbackbackup === 'true') {
    return;
  }

  target.src = defaultPoster;
  target.dataset.fallbackbackup = 'true';
}