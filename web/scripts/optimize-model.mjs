import { NodeIO } from "@gltf-transform/core";
import { ALL_EXTENSIONS } from "@gltf-transform/extensions";
import { dedup, prune, textureCompress } from "@gltf-transform/functions";
import sharp from "sharp";

// Repack a source GLB without hand-authoring or replacing any of its geometry.
// Credits and source URLs are preserved in public/models/ATTRIBUTION.md.
const [input, output] = process.argv.slice(2);
if (!input || !output)
  throw new Error(
    "Usage: node scripts/optimize-model.mjs input.glb output.glb",
  );
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const document = await io.read(input);
await document.transform(
  dedup(),
  prune(),
  textureCompress({
    encoder: sharp,
    targetFormat: "webp",
    resize: [2048, 2048],
    quality: 90,
  }),
);
await io.write(output, document);
