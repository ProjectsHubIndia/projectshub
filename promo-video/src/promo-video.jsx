import React from 'react';
import '@fontsource-variable/space-grotesk';
import {
  AbsoluteFill,
  Composition,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

const FPS = 30;
const SCENE_FRAMES = 180;
const INK = '#071525';
const CYAN = '#34c8f3';
const WHITE = '#f4f8fc';
const FONT = 'Space Grotesk, sans-serif';

const fullFrame = {
  width: 1920,
  height: 1080,
  overflow: 'hidden',
  fontFamily: FONT,
};

const entrance = (frame) => ({
  opacity: interpolate(frame, [0, 16, 164, 180], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }),
  transform: `translateY(${interpolate(frame, [0, 24], [26, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  })}px)`,
});

const Eyebrow = ({children}) => (
  <div
    style={{
      color: CYAN,
      fontSize: 18,
      fontWeight: 700,
      letterSpacing: 2.5,
      textTransform: 'uppercase',
    }}
  >
    {children}
  </div>
);

const FeatureScene = ({image, number, label, title, description, stat}) => {
  const frame = useCurrentFrame();
  const photoScale = interpolate(frame, [0, SCENE_FRAMES], [1.04, 1.12]);
  const contentStyle = entrance(frame);

  return (
    <AbsoluteFill style={{...fullFrame, backgroundColor: INK}}>
      <Img
        src={staticFile(image)}
        style={{
          position: 'absolute',
          left: 700,
          top: 0,
          width: 1220,
          height: 1080,
          objectFit: 'cover',
          objectPosition: 'center',
          transform: `scale(${photoScale})`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(90deg, #071525 0%, #071525 35%, rgba(7, 21, 37, 0.97) 42%, rgba(7, 21, 37, 0.7) 53%, rgba(7, 21, 37, 0.05) 76%)',
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            'radial-gradient(rgba(116, 174, 205, 0.24) 1px, transparent 1px)',
          backgroundSize: '32px 32px',
          opacity: 0.2,
          maskImage: 'linear-gradient(90deg, black 0%, transparent 65%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 132,
          top: 78,
          display: 'flex',
          alignItems: 'center',
          gap: 13,
          color: '#dbeaf5',
          fontSize: 19,
          fontWeight: 700,
          letterSpacing: 2,
          ...contentStyle,
        }}
      >
        <span style={{width: 11, height: 11, borderRadius: 99, background: CYAN}} />
        PROJECTSHUB
        <span style={{color: '#6d8499', fontWeight: 400}}> / </span>
        <span style={{color: '#91a9bb', fontWeight: 500}}>{number} — {label}</span>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 132,
          top: 248,
          width: 720,
          ...contentStyle,
        }}
      >
        <Eyebrow>{label}</Eyebrow>
        <h1
          style={{
            margin: '27px 0 24px',
            color: WHITE,
            fontSize: 94,
            lineHeight: 1.02,
            fontWeight: 700,
            letterSpacing: 0,
            whiteSpace: 'pre-line',
          }}
        >
          {title}
        </h1>
        <p
          style={{
            width: 660,
            margin: 0,
            color: '#bdcbd7',
            fontSize: 30,
            lineHeight: 1.45,
            fontWeight: 400,
          }}
        >
          {description}
        </p>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            marginTop: 43,
            padding: '13px 19px',
            border: '1px solid rgba(52, 200, 243, 0.45)',
            backgroundColor: 'rgba(18, 47, 67, 0.78)',
            color: WHITE,
            fontSize: 19,
            fontWeight: 700,
          }}
        >
          <span style={{color: CYAN, fontSize: 22}}>+</span>
          {stat}
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 132,
          bottom: 64,
          color: 'rgba(244, 248, 252, 0.75)',
          fontSize: 18,
          fontWeight: 600,
          letterSpacing: 1,
          ...contentStyle,
        }}
      >
        LEARN <span style={{color: CYAN}}>•</span> BUILD <span style={{color: CYAN}}>•</span> LAUNCH
      </div>
    </AbsoluteFill>
  );
};

const EndCard = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 20, 165, 180], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        ...fullFrame,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: INK,
        color: WHITE,
        opacity: reveal,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'radial-gradient(rgba(116, 174, 205, 0.23) 1px, transparent 1px)',
          backgroundSize: '34px 34px',
          opacity: 0.22,
          maskImage: 'linear-gradient(180deg, transparent, black 24%, black 78%, transparent)',
        }}
      />
      <div style={{position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        <Img
          src={staticFile('projectshub-logo.png')}
          style={{width: 690, height: 'auto', objectFit: 'contain', marginBottom: 28}}
        />
        <div style={{width: 92, height: 4, background: CYAN, margin: '0 0 35px'}} />
        <div style={{fontSize: 78, fontWeight: 700, lineHeight: 1.05, textAlign: 'center'}}>
          Start building.
        </div>
        <div
          style={{
            marginTop: 30,
            color: CYAN,
            fontSize: 31,
            fontWeight: 600,
            letterSpacing: 1,
          }}
        >
          projectshub.co.in
        </div>
        <div style={{marginTop: 40, color: '#a9bdcd', fontSize: 20, fontWeight: 500}}>
          AI projects <span style={{color: CYAN}}>·</span> Free tools <span style={{color: CYAN}}>·</span> Custom development
        </div>
      </div>
      <div style={{position: 'absolute', bottom: 55, color: '#8ba1b2', fontSize: 16, letterSpacing: 2}}>
        CONNECT <span style={{color: CYAN}}>•</span> COLLABORATE <span style={{color: CYAN}}>•</span> ACHIEVE
      </div>
    </AbsoluteFill>
  );
};

export const PromoVideo = () => (
  <AbsoluteFill style={{...fullFrame, backgroundColor: INK}}>
    <Sequence from={0} durationInFrames={SCENE_FRAMES}>
      <FeatureScene
        image="student.webp"
        number="01"
        label="LEARN BY BUILDING"
        title={'Learn AI\nby building.'}
        description="Hands-on AI and ML projects, source code, and mentor support."
        stat="50+ REAL-WORLD PROJECTS"
      />
    </Sequence>
    <Sequence from={SCENE_FRAMES} durationInFrames={SCENE_FRAMES}>
      <FeatureScene
        image="tools.webp"
        number="02"
        label="TOOLS THAT JUST WORK"
        title={'10+ AI tools.\nZero signup.'}
        description="Get useful work done with free tools, ready whenever you are."
        stat="FREE TO USE · NO SIGN-UP"
      />
    </Sequence>
    <Sequence from={SCENE_FRAMES * 2} durationInFrames={SCENE_FRAMES}>
      <FeatureScene
        image="business.webp"
        number="03"
        label="AI FOR BUSINESS"
        title={'Bring AI\nto the work.'}
        description="Custom AI development and automation, built around your business."
        stat="CUSTOM AI + AUTOMATION"
      />
    </Sequence>
    <Sequence from={SCENE_FRAMES * 3} durationInFrames={SCENE_FRAMES}>
      <EndCard />
    </Sequence>
  </AbsoluteFill>
);

export const RemotionRoot = () => (
  <Composition
    id="ProjectHubPromo"
    component={PromoVideo}
    durationInFrames={SCENE_FRAMES * 4}
    fps={FPS}
    width={1920}
    height={1080}
  />
);