import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  apiUrl,
  checkHealth,
  createAnnotation,
  LibraryImage,
  listDemoImages,
  listImages,
  searchImages,
  SearchResult,
  STATIC_DEMO,
  uploadImage,
} from "./api/client";

const emptyFilters = {
  garment_type: "",
  style: "",
  material: "",
  color: "",
  pattern: "",
  season: "",
  occasion: "",
  consumer_profile: "",
  location_context: "",
  continent: "",
  country: "",
  city: "",
  year: "",
  month: "",
  designer: "",
  annotation: "",
};

type FilterKey = keyof typeof emptyFilters;

export function App() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [images, setImages] = useState<LibraryImage[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImageId, setSelectedImageId] = useState<number | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [query, setQuery] = useState("red festive embroidered dress");
  const [filters, setFilters] = useState(emptyFilters);
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);
  const [searchStatus, setSearchStatus] = useState("");
  const [annotationNote, setAnnotationNote] = useState("");
  const [annotationTags, setAnnotationTags] = useState("");
  const [annotationStatus, setAnnotationStatus] = useState("");

  async function refreshLibrary() {
    const online = await checkHealth().catch(() => false);
    setApiOnline(online);
    const library = online ? await listImages() : STATIC_DEMO ? await listDemoImages() : [];
    setImages(library);
    setSelectedImageId((current) => current ?? library[0]?.id ?? null);
  }

  useEffect(() => {
    refreshLibrary().catch(() => setApiOnline(false));
    const timer = window.setInterval(() => {
      refreshLibrary().catch(() => setApiOnline(false));
    }, 3500);
    return () => window.clearInterval(timer);
  }, []);

  const selectedImage = useMemo(
    () => images.find((image) => image.id === selectedImageId) ?? images[0] ?? null,
    [images, selectedImageId],
  );

  const facets = useMemo(() => {
    const values: Record<FilterKey, Set<string>> = {
      garment_type: new Set(),
      style: new Set(),
      material: new Set(),
      color: new Set(),
      pattern: new Set(),
      season: new Set(),
      occasion: new Set(),
      consumer_profile: new Set(),
      location_context: new Set(),
      continent: new Set(),
      country: new Set(),
      city: new Set(),
      year: new Set(),
      month: new Set(),
      designer: new Set(),
      annotation: new Set(),
    };
    for (const image of images) {
      if (image.created_at) {
        const date = new Date(image.created_at);
        if (!Number.isNaN(date.getTime())) {
          values.year.add(String(date.getFullYear()));
          values.month.add(String(date.getMonth() + 1));
        }
      }
      for (const annotation of image.annotations) {
        if (annotation.created_by) values.designer.add(annotation.created_by);
        if (annotation.tags) values.annotation.add(annotation.tags);
      }
      if (!image.ai_metadata) continue;
      const locationParts = image.ai_metadata.location_context
        .split(/[>,/|-]/)
        .map((part) => part.trim())
        .filter(Boolean);
      if (locationParts[0] && locationParts[0] !== "unknown") values.continent.add(locationParts[0]);
      if (locationParts[1] && locationParts[1] !== "unknown") values.country.add(locationParts[1]);
      if (locationParts[2] && locationParts[2] !== "unknown") values.city.add(locationParts[2]);
      for (const key of Object.keys(values) as FilterKey[]) {
        if (key === "color") {
          for (const color of image.ai_metadata.color_palette) {
            if (color && color !== "unknown") values.color.add(color);
          }
          continue;
        }
        if (
          ["continent", "country", "city", "year", "month", "designer", "annotation"].includes(key)
        ) {
          continue;
        }
        const value = (image.ai_metadata as Record<string, unknown>)[key];
        if (typeof value === "string" && value && value !== "unknown") {
          values[key].add(value);
        }
      }
    }
    return Object.fromEntries(
      Object.entries(values).map(([key, value]) => [key, Array.from(value).sort()]),
    ) as Record<FilterKey, string[]>;
  }, [images]);

  const visibleImages = useMemo(() => {
    if (!searchResults) return images;
    const resultIds = new Set(searchResults.map((result) => result.image_id));
    return images.filter((image) => resultIds.has(image.id));
  }, [images, searchResults]);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) return;
    if (!apiOnline && STATIC_DEMO) {
      setUploadStatus("Static demo mode uses a prebuilt Pexels library. Run the backend locally to upload and classify new photos.");
      return;
    }

    setUploadStatus("Uploading image...");
    try {
      const response = await uploadImage(selectedFile);
      setUploadStatus(`Image #${response.image_id} uploaded. Classification is running.`);
      setSelectedFile(null);
      await refreshLibrary();
    } catch (error) {
      setUploadStatus(error instanceof Error ? error.message : "Upload failed.");
    }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearchStatus("Searching...");
    if (!apiOnline && STATIC_DEMO) {
      const response = searchLocalImages({
        images,
        query: query.trim(),
        filters,
        limit: 40,
      });
      setSearchResults(response);
      setSearchStatus(response.length ? `${response.length} matching image(s).` : "No matches yet.");
      return;
    }
    try {
      const response = await searchImages({
        query: query.trim() || undefined,
        garment_type: filters.garment_type || undefined,
        style: filters.style || undefined,
        material: filters.material || undefined,
        color: filters.color || undefined,
        pattern: filters.pattern || undefined,
        season: filters.season || undefined,
        occasion: filters.occasion || undefined,
        consumer_profile: filters.consumer_profile || undefined,
        location_context: filters.location_context || undefined,
        continent: filters.continent || undefined,
        country: filters.country || undefined,
        city: filters.city || undefined,
        year: filters.year ? Number(filters.year) : undefined,
        month: filters.month ? Number(filters.month) : undefined,
        designer: filters.designer || undefined,
        annotation: filters.annotation || undefined,
        limit: 40,
      });
      setSearchResults(response);
      setSearchStatus(response.length ? `${response.length} matching image(s).` : "No matches yet.");
    } catch (error) {
      setSearchStatus(error instanceof Error ? error.message : "Search failed.");
    }
  }

  async function handleAnnotation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedImage) return;
    if (!apiOnline && STATIC_DEMO) {
      const annotation = {
        id: Date.now(),
        note: annotationNote,
        tags: annotationTags,
        created_by: "designer",
      };
      setImages((current) =>
        current.map((image) =>
          image.id === selectedImage.id
            ? { ...image, annotations: [...image.annotations, annotation] }
            : image,
        ),
      );
      setAnnotationNote("");
      setAnnotationTags("");
      setAnnotationStatus("Annotation saved in this browser session.");
      return;
    }
    setAnnotationStatus("Saving annotation...");
    try {
      await createAnnotation(selectedImage.id, {
        note: annotationNote,
        tags: annotationTags,
      });
      setAnnotationNote("");
      setAnnotationTags("");
      setAnnotationStatus("Annotation saved.");
      await refreshLibrary();
    } catch (error) {
      setAnnotationStatus(error instanceof Error ? error.message : "Could not save annotation.");
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Fashion Garment Classification & Inspiration Web App</p>
          <h1>Searchable inspiration library for garment photos.</h1>
          <p className="lede">
            Upload field imagery, classify garments, filter structured attributes, and add designer notes.
          </p>
        </div>
        <div className={`status-pill ${apiOnline ? "online" : "offline"}`}>
          {apiOnline === null
            ? "Checking API"
            : apiOnline
              ? "API online"
              : STATIC_DEMO
                ? "Static demo"
                : "API offline"}
        </div>
      </section>

      <section className="workspace">
        <form className="panel upload-panel" onSubmit={handleUpload}>
          <div>
            <h2>Upload</h2>
            <p>
              {apiOnline || !STATIC_DEMO
                ? "Images are stored locally, classified in the background, and indexed for search."
                : "Static demo mode uses a prebuilt Pexels library. Run the backend locally to upload new photos."}
            </p>
          </div>
          <label className="drop-zone">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
            <span>{selectedFile ? selectedFile.name : "Choose a garment photo"}</span>
          </label>
          <button type="submit" disabled={!selectedFile || (!apiOnline && STATIC_DEMO)}>
            Upload and classify
          </button>
          {uploadStatus && <p className="form-message">{uploadStatus}</p>}
        </form>

        <form className="panel search-panel" onSubmit={handleSearch}>
          <div>
            <h2>Hybrid Search</h2>
            <p>Use a natural query, structured filters, or both.</p>
          </div>
          <label>
            Natural query
            <input value={query} onChange={(event) => setQuery(event.target.value)} />
          </label>
          <div className="filter-grid">
            {(Object.keys(filters) as FilterKey[]).map((key) => (
              <label key={key}>
                {key.replaceAll("_", " ")}
                <select
                  value={filters[key]}
                  onChange={(event) =>
                    setFilters((current) => ({ ...current, [key]: event.target.value }))
                  }
                >
                  <option value="">Any</option>
                  {facets[key].map((value) => (
                    <option value={value} key={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          <div className="button-row">
            <button type="submit">Search library</button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setSearchResults(null);
                setSearchStatus("Showing all images.");
                setFilters(emptyFilters);
              }}
            >
              Clear
            </button>
          </div>
          {searchStatus && <p className="form-message">{searchStatus}</p>}
        </form>
      </section>

      <section className="main-grid">
        <section className="library">
          <div className="section-heading">
            <div>
              <h2>Image Library</h2>
              <p>{visibleImages.length} image(s) visible.</p>
            </div>
          </div>
          <div className="image-grid">
            {visibleImages.length ? (
              visibleImages.map((image) => (
                <button
                  type="button"
                  className={`image-card ${selectedImage?.id === image.id ? "selected" : ""}`}
                  key={image.id}
                  onClick={() => setSelectedImageId(image.id)}
                >
                  <img src={apiUrl(image.image_url)} alt={image.original_filename} />
                  <span className={`image-status ${image.status}`}>{image.status}</span>
                  <strong>{image.ai_metadata?.garment_type ?? image.original_filename}</strong>
                  <small>{image.ai_metadata?.description ?? image.error_message ?? "Classification pending."}</small>
                  {image.ai_metadata?.color_palette?.length ? (
                    <span className="swatches">
                      {image.ai_metadata.color_palette.map((color) => (
                        <span className={`swatch ${color}`} key={color}>
                          {color}
                        </span>
                      ))}
                    </span>
                  ) : null}
                </button>
              ))
            ) : (
              <p className="empty-state">Upload a photo to start the inspiration library.</p>
            )}
          </div>
        </section>

        <aside className="panel detail-panel">
          {selectedImage ? (
            <>
              <img src={apiUrl(selectedImage.image_url)} alt={selectedImage.original_filename} />
              <div>
                <p className={`image-status ${selectedImage.status}`}>{selectedImage.status}</p>
                <h2>{selectedImage.original_filename}</h2>
              </div>

              {selectedImage.ai_metadata ? (
                <div className="metadata">
                  <h3>AI Metadata</h3>
                  <dl>
                    <div>
                      <dt>Garment</dt>
                      <dd>{selectedImage.ai_metadata.garment_type}</dd>
                    </div>
                    <div>
                      <dt>Style</dt>
                      <dd>{selectedImage.ai_metadata.style}</dd>
                    </div>
                    <div>
                      <dt>Material</dt>
                      <dd>{selectedImage.ai_metadata.material}</dd>
                    </div>
                    <div>
                      <dt>Colors</dt>
                      <dd>{selectedImage.ai_metadata.color_palette.join(", ")}</dd>
                    </div>
                    <div>
                      <dt>Pattern</dt>
                      <dd>{selectedImage.ai_metadata.pattern}</dd>
                    </div>
                    <div>
                      <dt>Season</dt>
                      <dd>{selectedImage.ai_metadata.season}</dd>
                    </div>
                    <div>
                      <dt>Occasion</dt>
                      <dd>{selectedImage.ai_metadata.occasion}</dd>
                    </div>
                    <div>
                      <dt>Customer</dt>
                      <dd>{selectedImage.ai_metadata.consumer_profile}</dd>
                    </div>
                    <div>
                      <dt>Location</dt>
                      <dd>{selectedImage.ai_metadata.location_context}</dd>
                    </div>
                  </dl>
                  <p>{selectedImage.ai_metadata.description}</p>
                  <p className="trend-note">{selectedImage.ai_metadata.trend_notes}</p>
                </div>
              ) : (
                <p className="empty-state">{selectedImage.error_message ?? "AI metadata is not ready yet."}</p>
              )}

              <div className="annotations">
                <h3>Designer Annotations</h3>
                {selectedImage.annotations.length ? (
                  selectedImage.annotations.map((annotation) => (
                    <article key={annotation.id} className="annotation">
                      <strong>{annotation.tags || "Observation"}</strong>
                      <p>{annotation.note}</p>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">No designer notes yet.</p>
                )}
              </div>

              <form className="annotation-form" onSubmit={handleAnnotation}>
                <label>
                  Tags
                  <input value={annotationTags} onChange={(event) => setAnnotationTags(event.target.value)} />
                </label>
                <label>
                  Notes
                  <textarea value={annotationNote} onChange={(event) => setAnnotationNote(event.target.value)} />
                </label>
                <button type="submit">Save annotation</button>
                {annotationStatus && <p className="form-message">{annotationStatus}</p>}
              </form>
            </>
          ) : (
            <p className="empty-state">Select an image to inspect AI metadata and add annotations.</p>
          )}
        </aside>
      </section>
    </main>
  );
}

function searchLocalImages({
  images,
  query,
  filters,
  limit,
}: {
  images: LibraryImage[];
  query: string;
  filters: typeof emptyFilters;
  limit: number;
}): SearchResult[] {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  return images
    .filter((image) => imageMatches(image, filters, terms))
    .slice(0, limit)
    .map((image) => ({
      image_id: image.id,
      score: null,
      description: image.ai_metadata?.description ?? null,
      garment_type: image.ai_metadata?.garment_type ?? null,
      style: image.ai_metadata?.style ?? null,
      material: image.ai_metadata?.material ?? null,
      color_palette: image.ai_metadata?.color_palette ?? null,
      pattern: image.ai_metadata?.pattern ?? null,
      season: image.ai_metadata?.season ?? null,
      occasion: image.ai_metadata?.occasion ?? null,
      consumer_profile: image.ai_metadata?.consumer_profile ?? null,
      location_context: image.ai_metadata?.location_context ?? null,
      created_at: image.created_at,
      designers: image.annotations
        .map((annotation) => annotation.created_by)
        .filter((designer): designer is string => Boolean(designer)),
      annotation_text: image.annotations
        .flatMap((annotation) => [annotation.tags, annotation.note])
        .filter(Boolean)
        .join(" "),
    }));
}

function imageMatches(image: LibraryImage, filters: typeof emptyFilters, terms: string[]): boolean {
  const metadata = image.ai_metadata;
  const annotationText = image.annotations
    .flatMap((annotation) => [annotation.tags, annotation.note, annotation.created_by])
    .filter(Boolean)
    .join(" ");
  const haystack = [
    image.original_filename,
    metadata?.garment_type,
    metadata?.style,
    metadata?.material,
    metadata?.color_palette.join(" "),
    metadata?.pattern,
    metadata?.season,
    metadata?.occasion,
    metadata?.consumer_profile,
    metadata?.trend_notes,
    metadata?.location_context,
    metadata?.description,
    annotationText,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  const created = image.created_at ? new Date(image.created_at) : null;
  const fieldChecks = [
    filters.garment_type && metadata?.garment_type,
    filters.style && metadata?.style,
    filters.material && metadata?.material,
    filters.pattern && metadata?.pattern,
    filters.season && metadata?.season,
    filters.occasion && metadata?.occasion,
    filters.consumer_profile && metadata?.consumer_profile,
    filters.location_context && metadata?.location_context,
    filters.continent && metadata?.location_context,
    filters.country && metadata?.location_context,
    filters.city && metadata?.location_context,
    filters.designer && annotationText,
    filters.annotation && annotationText,
  ];
  const filterValues = [
    filters.garment_type,
    filters.style,
    filters.material,
    filters.pattern,
    filters.season,
    filters.occasion,
    filters.consumer_profile,
    filters.location_context,
    filters.continent,
    filters.country,
    filters.city,
    filters.designer,
    filters.annotation,
  ].filter(Boolean);
  for (let index = 0; index < filterValues.length; index += 1) {
    const actual = fieldChecks[index];
    if (!actual || !actual.toLowerCase().includes(filterValues[index].toLowerCase())) return false;
  }
  if (filters.color && !metadata?.color_palette.some((color) => color.toLowerCase() === filters.color.toLowerCase())) {
    return false;
  }
  if (filters.year && (!created || String(created.getFullYear()) !== filters.year)) return false;
  if (filters.month && (!created || String(created.getMonth() + 1) !== filters.month)) return false;
  return terms.every((term) => haystack.includes(term));
}
