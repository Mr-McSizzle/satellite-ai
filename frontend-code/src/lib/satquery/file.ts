import type { ImageModality, SlotId, UploadedImage } from "./types";

const GEOTIFF_EXTENSIONS = [".tif", ".tiff"];
const STANDARD_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"];

function isGeoTiff(name: string): boolean {
  const lower = name.toLowerCase();
  return GEOTIFF_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

function isStandardImage(name: string): boolean {
  const lower = name.toLowerCase();
  return STANDARD_IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

function formatFromName(name: string): string {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  if (["tif", "tiff"].includes(ext)) return "GeoTIFF";
  if (ext === "png") return "PNG";
  if (["jpg", "jpeg"].includes(ext)) return "JPEG";
  return ext.toUpperCase() || "Unknown";
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function readImageFile(
  slot: SlotId,
  file: File,
  modality: ImageModality = "optical",
): Promise<UploadedImage> {
  return new Promise((resolve, reject) => {
    const mayCarryGeoMetadata = isGeoTiff(file.name);
    const format = formatFromName(file.name);

    if (!mayCarryGeoMetadata && !isStandardImage(file.name)) {
      reject(new Error(`"${file.name}" is not supported. Upload a .tif, .tiff, .png, .jpg or .jpeg file.`));
      return;
    }

    if (mayCarryGeoMetadata) {
      // For GeoTIFFs, browsers can't render them, so we skip image dimension detection.
      resolve({
        slot,
        file,
        name: file.name,
        modality,
        previewUrl: URL.createObjectURL(file),
        sizeBytes: file.size,
        format,
        width: 0,
        height: 0,
        mayCarryGeoMetadata: true,
      });
      return;
    }

    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      resolve({
        slot,
        file,
        name: file.name,
        modality,
        previewUrl: url,
        sizeBytes: file.size,
        format,
        width: img.naturalWidth,
        height: img.naturalHeight,
        mayCarryGeoMetadata: false,
      });
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error(`Could not read "${file.name}" as an image.`));
    };
    img.src = url;
  });
}
