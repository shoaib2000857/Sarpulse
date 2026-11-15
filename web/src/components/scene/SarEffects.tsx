import { useEffect, useMemo, useRef, type RefObject } from "react";
import { useFrame } from "@react-three/fiber";
import ThreeGlobe from "three-globe";
import { feature } from "topojson-client";
import countries from "world-atlas/countries-110m.json";
import {
  AdditiveBlending,
  DoubleSide,
  EdgesGeometry,
  Group,
  LineBasicMaterial,
  LineSegments,
  Material,
  Mesh,
  MeshBasicMaterial,
  MeshPhongMaterial,
  Object3D,
  CylinderGeometry,
  ShaderMaterial,
  Vector3,
} from "three";

/* Illustrative graphics. Land dots come from Natural Earth via world-atlas
   (public domain); globe, arcs and ripples come from three-globe. None of this
   is orbit, swath or observation data. */

export const smooth = (a: number, b: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

/** Blue "hologram" treatment: translucent fill plus glowing feature edges. */
export function toHologram(root: Object3D) {
  const fill = new MeshBasicMaterial({
    color: "#0a3a96",
    transparent: true,
    opacity: 0.28,
    depthWrite: false,
    blending: AdditiveBlending,
    side: DoubleSide,
  });
  const line = new LineBasicMaterial({
    color: "#3a95ff",
    transparent: true,
    opacity: 0.95,
    depthWrite: false,
    blending: AdditiveBlending,
  });
  const meshes: Mesh[] = [];
  root.traverse((o) => {
    if ((o as Mesh).isMesh) meshes.push(o as Mesh);
  });
  const hidden = new MeshBasicMaterial({ visible: false });
  meshes.forEach((m) => {
    // Hide glass via its material: Object3D.visible would also hide child meshes.
    if ((m.material as Material).name === "clear") {
      m.material = hidden;
      return;
    }
    m.material = fill;
    m.add(new LineSegments(new EdgesGeometry(m.geometry, 24), line));
  });
}

/** Dark dotted-continent look from the reference; off = real NASA Earth colours. */
const DOTTED_LAND = false;

type HexMesh = Mesh<never, MeshPhongMaterial>;
const landFeatures = (() => {
  const topo = countries as unknown as Parameters<typeof feature>[0];
  const fc = feature(topo, (topo as any).objects.countries) as any;
  // Antarctica spans the pole and North Korea's 110m polygon is rejected by
  // h3's polygonToCells; both are skipped (decorative dots only).
  const skip = new Set(["Antarctica", "North Korea"]);
  return fc.features.filter((f: any) => !skip.has(f.properties?.name));
})();

/**
 * Dark planet with a dotted-continent layer, orbit streaks and a blue
 * atmosphere. Fades between chapters; lives inside the Earth group (radius 0.5).
 */
export function DotGlobe({ progress }: { progress: RefObject<number> }) {
  const globe = useMemo(() => {
    const g = new ThreeGlobe({ animateIn: false, waitForGlobeReady: false })
      .globeMaterial(
        new MeshPhongMaterial({
          color: "#03060d",
          emissive: "#050b18",
          shininess: 4,
          specular: "#0b1a33",
        }),
      )
      .showGlobe(DOTTED_LAND)
      .atmosphereColor("#4aa8ff")
      .atmosphereAltitude(0.24)
      .hexPolygonResolution(3)
      .hexPolygonMargin(0.42)
      .hexPolygonUseDots(true)
      .hexPolygonColor(() => "#8da3c0")
      .arcsData(
        [
          [40, -150, -30, 20],
          [60, -20, -20, 140],
          [10, 80, 55, -120],
          [-35, -70, 35, 110],
          [25, 160, -45, -10],
        ].map(([startLat, startLng, endLat, endLng]) => ({
          startLat,
          startLng,
          endLat,
          endLng,
        })),
      )
      .arcColor(() => ["rgba(50,120,255,0)", "rgba(140,205,255,0.95)"])
      .arcStroke(0.22)
      .arcAltitude(0.22)
      .arcDashLength(0.32)
      .arcDashGap(2.4)
      .arcDashAnimateTime(4200);
    return g;
  }, []);
  const hex = useRef<HexMesh[]>([]),
    arcs = useRef<Object3D[]>([]),
    shown = useRef(false),
    heroAtmosphere = useRef(false);
  const landReady = useRef(false);
  useEffect(() => {
    // The dotted land is hidden in the hero, so build it just after the first frame.
    // Dotted land is off in the real-Earth colour scheme; flip DOTTED_LAND to restore it.
    const id = window.setTimeout(() => {
      if (!DOTTED_LAND) return;
      globe.hexPolygonsData(landFeatures);
      landReady.current = true;
    }, 600);
    return () => {
      window.clearTimeout(id);
      (globe as unknown as { _destructor?: () => void })._destructor?.();
    };
  }, [globe]);
  useFrame(() => {
    if (landReady.current && !hex.current.length) {
      globe.traverse((o) => {
        const type = (o as Object3D & { __globeObjType?: string })
          .__globeObjType;
        if (type === "hexPolygon") {
          const m = o as HexMesh;
          m.material.transparent = true;
          m.material.opacity = 0;
          hex.current.push(m);
        } else if (type === "arc") arcs.current.push(o);
      });
    }
    const t = progress.current * 4;
    const dots = smooth(1.15, 1.9, t) * (1 - smooth(3.1, 3.8, t));
    hex.current.forEach((m) => {
      m.visible = dots > 0.01;
      m.material.opacity = dots;
    });
    const streaks = smooth(1.4, 2, t) * (1 - smooth(3, 3.6, t)) > 0.02;
    arcs.current.forEach((a) => (a.visible = streaks));
    // Hero: thin grey rim light (camera sits outside a slim shell); later a wide blue halo.
    const hero = t < 0.6;
    if (hero !== heroAtmosphere.current) {
      heroAtmosphere.current = hero;
      globe
        .atmosphereAltitude(hero ? 0.07 : 0.24)
        .atmosphereColor(hero ? "#6fb4ff" : "#4aa8ff");
    }
    const wantGlobe = DOTTED_LAND && t < 3.7;
    if (wantGlobe !== shown.current) {
      shown.current = wantGlobe;
      globe.showGlobe(wantGlobe);
    }
  });
  return <primitive object={globe} scale={0.005} rotation-y={0.8} />;
}

const beamMaterial = () =>
  new ShaderMaterial({
    transparent: true,
    side: DoubleSide,
    depthWrite: false,
    blending: AdditiveBlending,
    uniforms: { uOpacity: { value: 0 }, uTime: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform float uOpacity; uniform float uTime; varying vec2 vUv;
      void main(){
        float fade = smoothstep(0.0,0.08,vUv.y) * (0.25 + 0.75*vUv.y);
        float band = 0.55 + 0.45*sin((vUv.y*26.0) - uTime*7.0);
        float edge = 0.6 + 0.4*sin(vUv.x*6.2831*2.0);
        gl_FragColor = vec4(0.1,0.63,1.0,1.0) * fade * band * edge * uOpacity * 1.2;
      }`,
  });

/**
 * The SAR idea in one picture: the sensor illuminates the ground with its own
 * radar beam, and echoes ripple back from the surface. The ripples are
 * three-globe rings on a second, surface-less globe aimed at the footprint.
 */
export function SarBeam({
  spacecraft,
  earth,
  progress,
  motion,
}: {
  spacecraft: RefObject<Group | null>;
  earth: RefObject<Group | null>;
  progress: RefObject<number>;
  motion: boolean;
}) {
  const beam = useRef<Group>(null),
    cone = useRef<Mesh>(null),
    footprint = useRef<Group>(null);
  const bMat = useMemo(beamMaterial, []);
  const echo = useMemo(
    () =>
      new ThreeGlobe({ animateIn: false })
        .showGlobe(false)
        .showAtmosphere(false)
        .ringsData([{ lat: 0, lng: 0 }])
        .ringColor(
          () => (t: number) => `rgba(120,210,255,${Math.max(0, 1 - t)})`,
        )
        .ringMaxRadius(7)
        .ringPropagationSpeed(2.4)
        .ringRepeatPeriod(1000),
    [],
  );
  useEffect(
    () => () => {
      (echo as unknown as { _destructor?: () => void })._destructor?.();
    },
    [echo],
  );
  const geometry = useMemo(() => {
    const g = new CylinderGeometry(0.02, 0.5, 1, 40, 12, true);
    g.translate(0, -0.5, 0);
    g.rotateX(-Math.PI / 2);
    return g;
  }, []);
  const dir = useMemo(() => new Vector3(0.5, -0.32, 0.8).normalize(), []);
  const tmp = useMemo(() => ({ target: new Vector3(), z: new Vector3(0, 0, 1) }), []);
  useFrame(({ clock }) => {
    const p = progress.current,
      pose = spacecraft.current,
      planet = earth.current;
    if (!beam.current || !footprint.current || !pose || !planet) return;
    const a = smooth(0.86, 0.97, p);
    beam.current.visible = footprint.current.visible = a > 0.01;
    if (a <= 0.01) return;
    const radius = 0.5 * planet.scale.x;
    tmp.target
      .copy(planet.position)
      .addScaledVector(dir, radius * 1.004);
    beam.current.position.copy(pose.position);
    beam.current.lookAt(tmp.target);
    cone.current?.scale.set(
      1,
      1,
      beam.current.position.distanceTo(tmp.target),
    );
    bMat.uniforms.uOpacity.value = a;
    bMat.uniforms.uTime.value = motion ? clock.elapsedTime : 0;
    footprint.current.position.copy(tmp.target);
    footprint.current.quaternion.setFromUnitVectors(tmp.z, dir);
    footprint.current.scale.setScalar(radius * 0.01);
  });
  return (
    <>
      <group ref={beam} visible={false}>
        <mesh ref={cone} geometry={geometry} material={bMat} />
      </group>
      {/* ThreeGlobe units: radius 100, ring sits on the surface at lat 0 / lng 0 (+Z). */}
      <group ref={footprint} visible={false}>
        <group position={[0, 0, -100]}>
          <primitive object={echo} />
        </group>
      </group>
    </>
  );
}
