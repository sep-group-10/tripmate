import { useState } from "react";
import { ChevronLeft, ChevronRight, ImageOff } from "lucide-react";

/** Photo carousel for the top of an EntityCard. Shows a placeholder when
 * there are no photos; arrows/dots only appear with more than one, and
 * stop click propagation so they don't trigger the card's own onClick
 * (which opens Edit). */
function EntityPhotoCarousel({ photoUrls, name }) {
  const photos = photoUrls || [];
  const [index, setIndex] = useState(0);

  if (photos.length === 0) {
    return (
      <div className="-mx-5 -mt-5 flex aspect-video items-center justify-center rounded-t-lg border-b border-border bg-muted-300">
        <ImageOff size={24} aria-hidden="true" className="text-muted-500" />
      </div>
    );
  }

  const goTo = (event, nextIndex) => {
    event.stopPropagation();
    setIndex((nextIndex + photos.length) % photos.length);
  };

  return (
    <div className="relative -mx-5 -mt-5 aspect-video overflow-hidden rounded-t-lg bg-muted-200">
      <img
        src={photos[index]}
        alt={name ? `${name} photo ${index + 1}` : ""}
        className="h-full w-full object-cover"
        loading="lazy"
      />

      {photos.length > 1 && (
        <>
          <button
            type="button"
            onClick={(event) => goTo(event, index - 1)}
            aria-label="Previous photo"
            className="absolute top-1/2 left-2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full bg-ink/50 text-white"
          >
            <ChevronLeft size={16} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={(event) => goTo(event, index + 1)}
            aria-label="Next photo"
            className="absolute top-1/2 right-2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full bg-ink/50 text-white"
          >
            <ChevronRight size={16} aria-hidden="true" />
          </button>
          <div className="absolute bottom-2 left-1/2 flex -translate-x-1/2 gap-1.5">
            {photos.map((url, dotIndex) => (
              <button
                key={url}
                type="button"
                onClick={(event) => goTo(event, dotIndex)}
                aria-label={`Go to photo ${dotIndex + 1}`}
                className={`h-1.5 w-1.5 rounded-full ${
                  dotIndex === index ? "bg-white" : "bg-white/50"
                }`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default EntityPhotoCarousel;
