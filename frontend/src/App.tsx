import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  apiUrl,
  checkHealth,
  createAnnotation,
  LibraryImage,
  listImages,
  searchImages,
  SearchResult,
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
    if (!online) return;
    const library = await listImages();
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
    };
    for (const image of images) {
      if (!image.ai_metadata) continue;
      for (const key of Object.keys(values) as FilterKey[]) {
        if (key === "color") {
          for (const color of image.ai_metadata.color_palette) {
            if (color && color !== "unknown") values.color.add(color);
          }
          continue;
        }
        const value = image.ai_metadata[key];
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
          <p className="eyebrow">Atelier Lens AI</p>
          <h1>Searchable inspiration library for garment photos.</h1>
          <p className="lede">
            Upload field imagery, classify garments, filter structured attributes, and add designer notes.
          </p>
        </div>
        <div className={`status-pill ${apiOnline ? "online" : "offline"}`}>
          {apiOnline === null ? "Checking API" : apiOnline ? "API online" : "API offline"}
        </div>
      </section>

      <section className="workspace">
        <form className="panel upload-panel" onSubmit={handleUpload}>
          <div>
            <h2>Upload</h2>
            <p>Images are stored locally, classified in the background, and indexed for search.</p>
          </div>
          <label className="drop-zone">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
            <span>{selectedFile ? selectedFile.name : "Choose a garment photo"}</span>
          </label>
          <button type="submit" disabled={!selectedFile}>
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
                {key.replace("_", " ")}
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
