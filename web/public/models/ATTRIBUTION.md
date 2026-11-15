# Loaded 3D presentation assets

## NASA SMAP spacecraft

Source: https://smap.jpl.nasa.gov/resources/99/smap-3d-model/.
Credit: NASA Visualization Technology Applications and Development (VTAD).
Original download: the `SMAP.glb` download linked by that page (approximately 8.6 MiB).

This is **SMAP, not NISAR**. It is used only as a labeled Earth-observation spacecraft presentation reference; it does not identify the source of any observations in SARPulse or imply NASA endorsement. No geometry is invented or relabeled as NISAR hardware.

## NASA Earth model

Source: https://science.nasa.gov/learn/heat/resource/earth-3d-model/.
Original: https://assets.science.nasa.gov/content/dam/science/psd/solar/2023/09/e/Earth_1_12756.glb.
Credit: NASA/JPL-Caltech.

The Earth model is illustrative historical visual context, not SAR data, current weather, acquisition coverage, or an analysis output.

NASA asset use guidance: https://science.nasa.gov/3d-resources/ and https://www.nasa.gov/nasa-brand-center/images-and-media/.

Both source GLBs were repacked with glTF Transform: duplicate/unreferenced data removed; embedded textures resized to a maximum of 2048 pixels and encoded as WebP (quality 90). The source geometry and material assignments are retained. The reproducible tool is `web/scripts/optimize-model.mjs`. Source originals are not duplicated in the repository.

## Studio HDR environment

`public/environment/studio.hdr`: Studio Small 03 by Greg Zaal / Poly Haven, 1K HDR.
Source: https://polyhaven.com/a/studio_small_03.
Download: https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_03_1k.hdr.
License: CC0 — https://polyhaven.com/license.

## Fonts and reference

Manrope is supplied through the Fontsource package under its bundled SIL Open Font License. It is an openly licensed visual substitute; EnduroSat's Magnetik font files and proprietary scene/model assets have not been redistributed. EnduroSat's public page was inspected for layout, proportions and interaction structure; its source implementation was not copied into this application.
