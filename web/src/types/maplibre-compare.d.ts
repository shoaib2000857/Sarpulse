declare module "@maplibre/maplibre-gl-compare" {
  import type { Map } from "maplibre-gl";
  export default class Compare {
    constructor(
      before: Map,
      after: Map,
      container: string | HTMLElement,
      options?: {
        orientation?: "vertical" | "horizontal";
        mousemove?: boolean;
      },
    );
    currentPosition: number;
    setSlider(position: number): void;
    on(
      event: "slideend",
      listener: (event: { currentPosition: number }) => void,
    ): this;
    remove(): void;
  }
}
