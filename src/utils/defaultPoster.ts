import defaultPoster from '@/assets/defaultPoster.webp';
import posterDEF from '@/assets/posterDEF.jpg'
export function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement | null;
  if (target) {
    target.src = posterDEF;
  }
}