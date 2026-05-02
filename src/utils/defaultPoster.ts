export function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement | null;
  if (target) {
    target.src = '/defaultPoster.webp';
  }
}