import {
  Component,
  forwardRef,
  Suspense,
  useEffect,
  useImperativeHandle,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  Center,
  Environment,
  Float,
  PresentationControls,
  Resize,
  Stars,
  useGLTF,
  useProgress,
} from "@react-three/drei";
import { ACESFilmicToneMapping, Group, Mesh, type Material } from "three";
import gsap from "gsap";
import { DotGlobe, SarBeam, toHologram } from "./SarEffects";

export type SceneHandle = {
  invalidate: () => void;
  rotate: (amount: number) => void;
  reset: () => void;
};
type Props = { progress: RefObject<number>; motion: boolean };
const base = import.meta.env.BASE_URL;
const modelUrl = `${base}models/smap.glb`,
  earthUrl = `${base}models/earth.glb`;

// Geometry and textures come from authored NASA GLBs, loaded by Drei. Globe dots,
// atmosphere, arcs and ripples come from three-globe.
function ModelAsset({ url, holo }: { url: string; holo?: boolean }) {
  const gltf = useGLTF(url, false);
  const object = useMemo(() => {
    const clone = gltf.scene.clone(true);
    if (holo) toHologram(clone);
    return clone;
  }, [gltf.scene, holo]);
  return (
    <Center>
      <Resize>
        <primitive object={object} dispose={null} />
      </Resize>
    </Center>
  );
}

/** Real NASA Earth, shown in every chapter. */
function EarthModel() {
  const gltf = useGLTF(earthUrl, false);
  const object = useMemo(() => {
    const clone = gltf.scene.clone(true);
    clone.traverse((o) => {
      const m = o as Mesh;
      if (m.isMesh) {
        m.material = (m.material as Material).clone();
        m.material.transparent = true;
      }
    });
    return clone;
  }, [gltf.scene]);
  return (
    <group rotation-y={3.5}>
      <Center>
        <Resize>
          <primitive object={object} dispose={null} />
        </Resize>
      </Center>
    </group>
  );
}

type Pose = {
  x: number;
  y: number;
  z?: number;
  scale: number;
  rx: number;
  ry: number;
  rz: number;
};

function LoadedScene({
  progress,
  motion,
  rotation,
  resetVersion,
  bridge,
  onReady,
}: {
  progress: RefObject<number>;
  motion: boolean;
  rotation: RefObject<number>;
  resetVersion: number;
  bridge: RefObject<() => void>;
  onReady: () => void;
}) {
  const spacecraft = useRef<Group>(null),
    keyboardRotation = useRef<Group>(null),
    earth = useRef<Group>(null);
  const { invalidate, size } = useThree();
  const mobile = size.width < 768;
  const ready = useRef(false);
  const choreography = useRef<gsap.core.Timeline | null>(null);
  useEffect(() => {
    bridge.current = invalidate;
    return () => {
      bridge.current = () => {};
    };
  }, [bridge, invalidate]);
  // Spacecraft per chapter: hero, challenge, solution, two steps (leaves frame), finale.
  const poses = useMemo<Pose[]>(
    () =>
      mobile
        ? [
            { x: 0, y: -0.65, scale: 2.6, rx: 0.16, ry: -0.75, rz: -0.16 },
            { x: 1.4, y: 1.4, scale: 1.5, rx: 0.25, ry: 0.5, rz: 0.2 },
            { x: 1.5, y: 2.2, scale: 1, rx: -0.2, ry: 1.9, rz: -0.25 },
            { x: 6, y: 3, scale: 0.4, rx: 0.3, ry: 2.8, rz: 0.7 },
            { x: 1.2, y: 1.6, z: -1, scale: 0.9, rx: 0, ry: 3.5, rz: -0.2 },
          ]
        : [
            { x: 2.4, y: 0, scale: 5.25, rx: 0.12, ry: -0.75, rz: -0.16 },
            { x: 4.3, y: 1.6, scale: 2.6, rx: 0.3, ry: 0.5, rz: 0.2 },
            { x: 4.9, y: 2.4, scale: 1.7, rx: -0.2, ry: 1.9, rz: -0.25 },
            { x: 9.5, y: 3.2, scale: 0.5, rx: 0.3, ry: 2.8, rz: 0.7 },
            { x: 3.9, y: 0.7, z: -1, scale: 1.2, rx: 0, ry: 3.5, rz: -0.2 },
          ],
    [mobile],
  );
  // Planet per chapter: limb at the bottom, dark limb right, dotted globe, centred globe, lit Earth.
  const planet = useMemo(
    () =>
      mobile
        ? [
            { x: 0, y: -22, z: -6, s: 42 },
            { x: 8, y: -4, z: -6, s: 14 },
            { x: 0.6, y: -0.6, z: -6, s: 7 },
            { x: 0, y: -0.2, z: -6, s: 6.4 },
            { x: 0, y: 0, z: -6, s: 4.4 },
          ]
        : [
            { x: 0, y: -37, z: -6, s: 70 },
            { x: 13.5, y: -2, z: -6, s: 22 },
            { x: 1.6, y: -0.2, z: -6, s: 10.2 },
            { x: 0, y: 0, z: -6, s: 9 },
            { x: 0, y: 0.1, z: -6, s: 6.2 },
          ],
    [mobile],
  );
  useLayoutEffect(() => {
    const pose = spacecraft.current,
      world = earth.current;
    if (!pose || !world) return;
    const timeline = gsap.timeline({ paused: true });
    const first = poses[0];
    gsap.set(pose.position, { x: first.x, y: first.y, z: first.z ?? 0 });
    gsap.set(pose.rotation, { x: first.rx, y: first.ry, z: first.rz });
    pose.scale.setScalar(first.scale);
    world.position.set(planet[0].x, planet[0].y, planet[0].z);
    world.scale.setScalar(planet[0].s);
    poses.slice(1).forEach((p, i) => {
      timeline.to(
        pose.position,
        { x: p.x, y: p.y, z: p.z ?? 0, duration: 1, ease: "power2.inOut" },
        i,
      );
      timeline.to(
        pose.rotation,
        { x: p.rx, y: p.ry, z: p.rz, duration: 1, ease: "power2.inOut" },
        i,
      );
      timeline.to(
        pose.scale,
        {
          x: p.scale,
          y: p.scale,
          z: p.scale,
          duration: 1,
          ease: "power2.inOut",
        },
        i,
      );
    });
    planet.slice(1).forEach((p, i) => {
      timeline.to(
        world.position,
        { x: p.x, y: p.y, z: p.z, duration: 1, ease: "power2.inOut" },
        i,
      );
      timeline.to(
        world.scale,
        { x: p.s, y: p.s, z: p.s, duration: 1, ease: "power2.inOut" },
        i,
      );
    });
    timeline.to(world.rotation, { y: 0.9, duration: 4, ease: "none" }, 0);
    choreography.current = timeline;
    return () => {
      timeline.kill();
      choreography.current = null;
    };
  }, [poses, planet]);
  useFrame(() => {
    if (!ready.current) {
      ready.current = true;
      requestAnimationFrame(onReady);
      invalidate();
    }
    choreography.current?.progress(progress.current);
    if (keyboardRotation.current)
      keyboardRotation.current.rotation.y = rotation.current;
    if (motion) invalidate();
  });
  return (
    <>
      <Environment
        files={`${base}environment/studio.hdr`}
        environmentIntensity={1.1}
      />
      <ambientLight intensity={0.45} />
      <directionalLight position={[-4, 5, 6]} intensity={2.5} color="#eaf2ff" />
      <directionalLight position={[4, 1, -4]} intensity={2} color="#81bdff" />
      <Stars
        radius={30}
        depth={12}
        count={5000}
        factor={2.4}
        saturation={0}
        fade
        speed={motion ? 0.5 : 0}
      />
      <group ref={spacecraft}>
        <PresentationControls
          key={resetVersion}
          global
          polar={[-0.5, 0.5]}
          azimuth={[-Infinity, Infinity]}
          speed={1.2}
          damping={0.15}
        >
          <Float
            enabled={motion}
            speed={0.7}
            rotationIntensity={0.1}
            floatIntensity={0.1}
            autoInvalidate={motion}
          >
            <group ref={keyboardRotation}>
              <ModelAsset url={modelUrl} />
            </group>
          </Float>
        </PresentationControls>
      </group>
      <group ref={earth}>
        <DotGlobe progress={progress} />
        <EarthModel />
      </group>
      <SarBeam
        spacecraft={spacecraft}
        earth={earth}
        progress={progress}
        motion={motion}
      />
    </>
  );
}

function LoadingProgress() {
  const { progress } = useProgress();
  return (
    <div className="orbital-loading">
      <span />
      <div>
        Loading 3D assets <b>{Math.round(progress)}%</b>
        <i style={{ transform: `scaleX(${progress / 100})` }} />
      </div>
    </div>
  );
}
function Unavailable() {
  return (
    <div className="orbital-static" role="status">
      <span>
        3D view unavailable. The investigation below remains accessible.
      </span>
    </div>
  );
}
class SceneBoundary extends Component<
  { children: ReactNode; onFailure: () => void },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onFailure();
  }
  render() {
    return this.state.failed ? <Unavailable /> : this.props.children;
  }
}

const OrbitalScene = forwardRef<SceneHandle, Props>(function OrbitalScene(
  { progress, motion },
  ref,
) {
  const root = useRef<HTMLDivElement>(null),
    bridge = useRef<() => void>(() => {}),
    rotation = useRef(0);
  const [status, setStatus] = useState<"loading" | "ready" | "unavailable">(
    "loading",
  );
  const [visible, setVisible] = useState(true),
    [resetVersion, setResetVersion] = useState(0);
  useImperativeHandle(
    ref,
    () => ({
      invalidate: () => bridge.current(),
      rotate: (amount) => {
        rotation.current += amount;
        bridge.current();
      },
      reset: () => {
        rotation.current = 0;
        setResetVersion((v) => v + 1);
        bridge.current();
      },
    }),
    [],
  );
  useEffect(() => {
    if (!root.current) return;
    const target = root.current;
    const observer = new IntersectionObserver(([entry]) =>
      setVisible(entry.isIntersecting && !document.hidden),
    );
    observer.observe(target);
    const onVisibility = () =>
      setVisible(
        !document.hidden &&
          target.getBoundingClientRect().bottom > 0 &&
          target.getBoundingClientRect().top < innerHeight,
      );
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      observer.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);
  const failure = () => setStatus("unavailable");
  return (
    <div
      className="orbital-scene"
      ref={root}
      data-scene-status={status}
      data-model-source="NASA SMAP GLB"
      role="img"
      aria-label="Loaded NASA SMAP spacecraft and Earth 3D models. SMAP is a presentation reference, not NISAR or a live orbit."
    >
      <SceneBoundary onFailure={failure}>
        <Canvas
          frameloop={status === "ready" && visible && motion ? "always" : "demand"}
          dpr={[1, innerWidth < 768 ? 1.25 : 1.5]}
          camera={{ position: [0, 0, 11.5], fov: 34, near: 0.1, far: 80 }}
          gl={{
            antialias: true,
            alpha: false,
            toneMapping: ACESFilmicToneMapping,
            toneMappingExposure: 1,
          }}
          fallback={<Unavailable />}
          onCreated={({ gl }) => {
            gl.setClearColor("#000000");
            gl.domElement.setAttribute("aria-hidden", "true");
            gl.domElement.addEventListener("webglcontextlost", failure, {
              once: true,
            });
          }}
        >
          <Suspense fallback={null}>
            <LoadedScene
              progress={progress}
              motion={motion && visible}
              rotation={rotation}
              resetVersion={resetVersion}
              bridge={bridge}
              onReady={() => setStatus("ready")}
            />
          </Suspense>
        </Canvas>
      </SceneBoundary>
      {status === "loading" && <LoadingProgress />}
    </div>
  );
});
export default OrbitalScene;
