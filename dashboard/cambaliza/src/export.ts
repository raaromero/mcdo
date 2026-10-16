// Shared PNG export helpers: SVG → image (with computed styles inlined) and a download trigger.

/** Rasterize an on-page SVG, copying its computed styles so CSS-variable colors survive serialization. */
export async function svgImage(svg: SVGSVGElement): Promise<HTMLImageElement | null> {
  const clone = svg.cloneNode(true) as SVGSVGElement;
  const src = svg.querySelectorAll("*");
  clone.querySelectorAll("*").forEach((el, i) => {
    const st = getComputedStyle(src[i]);
    for (const prop of ["fill", "stroke", "stroke-width", "stroke-dasharray", "opacity", "font-size", "font-weight", "font-family", "text-anchor"])
      (el as SVGElement).style.setProperty(prop, st.getPropertyValue(prop));
  });
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const box = svg.getBoundingClientRect();
  clone.setAttribute("width", String(box.width));
  clone.setAttribute("height", String(box.height));
  const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(clone)], { type: "image/svg+xml" }));
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null);
    img.src = url;
  });
}

export async function download(canvas: HTMLCanvasElement, filename: string) {
  const blob = await new Promise<Blob | null>((r) => canvas.toBlob(r, "image/png"));
  if (!blob) return;
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
