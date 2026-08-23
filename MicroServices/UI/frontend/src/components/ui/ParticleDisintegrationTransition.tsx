'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

export interface Particle {
  origX: number;
  origY: number;
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  targetX: number;
  targetY: number;
  targetZ: number;
  rotX: number;
  rotY: number;
  rotZ: number;
  vRotX: number;
  vRotY: number;
  vRotZ: number;
  size: number;
  r: number;
  g: number;
  b: number;
  baseAlpha: number;
  alpha: number;
  elemType: 'text' | 'button' | 'card' | 'icon' | 'badge' | 'ambient' | 'frame';
  shape: 'rect' | 'dot' | 'shard';
  waveDelay: number;
  active: boolean;
}

interface DissolvingElement {
  el: HTMLElement | SVGElement;
  delay: number;
  driftX: number;
  driftY: number;
  driftZ: number;
  rot: number;
  dissolved: boolean;
  origOpacity: string;
  origTransform: string;
  origFilter: string;
  origTransition: string;
}

// Global utility helper to trigger from anywhere
export const triggerDisintegration = (e?: React.MouseEvent | MouseEvent | { clientX: number; clientY: number }) => {
  const cx = e ? e.clientX : (typeof window !== 'undefined' ? window.innerWidth / 2 : 500);
  const cy = e ? e.clientY : (typeof window !== 'undefined' ? window.innerHeight / 2 : 400);
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('trigger-disintegration', { detail: { x: cx, y: cy } }));
  }
};

interface ParticleDisintegrationTransitionProps {
  targetHref?: string;
  triggerRef?: React.MutableRefObject<((clickEvent?: React.MouseEvent | MouseEvent) => void) | null>;
}

export const ParticleDisintegrationTransition: React.FC<ParticleDisintegrationTransitionProps> = ({
  targetHref = '/dashboard',
  triggerRef,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isRunning, setIsRunning] = useState(false);
  const router = useRouter();
  const animFrameRef = useRef<number | null>(null);
  const isTransitioningRef = useRef(false);
  const dissolvingElementsRef = useRef<DissolvingElement[]>([]);

  // Subtle sci-fi bass synth sound
  const playCinematicAudio = () => {
    try {
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (!AudioContextClass) return;
      const ctx = new AudioContextClass();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(950, ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 1.2);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(170, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(45, ctx.currentTime + 1.2);

      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 1.5);
    } catch {
      // Audio policies fallback
    }
  };

  // Sample actual visible DOM elements + the Big Outer Frame to extract authentic particle colors & positions
  const samplePageElements = (clickX: number, clickY: number): Particle[] => {
    const particles: Particle[] = [];
    const dissolvingElements: DissolvingElement[] = [];
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // Target reconstruction coordinates for Dashboard UI
    const topBarTargets = { x: vw / 2, y: 28, width: Math.min(vw * 0.9, 1300), height: 48 };
    const ribbonW = Math.min(vw * 0.9, 1200);
    const cardW = ribbonW / 6 - 12;
    const startX = (vw - ribbonW) / 2;
    const ribbonCards: { x: number; y: number; width: number; height: number }[] = [];
    for (let i = 0; i < 6; i++) {
      ribbonCards.push({ x: startX + i * (cardW + 12) + cardW / 2, y: 140, width: cardW, height: 75 });
    }
    const funnelCard = { x: vw * 0.38, y: 380, width: vw * 0.52, height: 320 };
    const activityCard = { x: vw * 0.76, y: 380, width: vw * 0.22, height: 320 };
    const bottomDock = { x: vw / 2, y: vh - 35, width: Math.min(vw * 0.65, 680), height: 48 };

    const getReconstructTarget = (i: number): { x: number; y: number; z: number } => {
      const rand = (i * 7919) % 100;
      if (rand < 20) {
        const spread = (Math.random() - 0.5) * topBarTargets.width;
        return { x: topBarTargets.x + spread, y: topBarTargets.y + (Math.random() - 0.5) * topBarTargets.height, z: 0 };
      } else if (rand < 50) {
        const card = ribbonCards[i % ribbonCards.length];
        return {
          x: card.x + (Math.random() - 0.5) * card.width,
          y: card.y + (Math.random() - 0.5) * card.height,
          z: 0
        };
      } else if (rand < 75) {
        return {
          x: funnelCard.x + (Math.random() - 0.5) * funnelCard.width,
          y: funnelCard.y + (Math.random() - 0.5) * funnelCard.height,
          z: 0
        };
      } else if (rand < 88) {
        return {
          x: activityCard.x + (Math.random() - 0.5) * activityCard.width,
          y: activityCard.y + (Math.random() - 0.5) * activityCard.height,
          z: 0
        };
      } else {
        const spread = (Math.random() - 0.5) * bottomDock.width;
        return { x: bottomDock.x + spread, y: bottomDock.y + (Math.random() - 0.5) * bottomDock.height, z: 0 };
      }
    };

    // 1. Explicitly Sample the BIG GLASS FRAME and SVG Mask
    const bigFrame = document.getElementById('landing-glass-frame');
    const svgMask = document.getElementById('landing-svg-mask');

    if (bigFrame) {
      const fRect = bigFrame.getBoundingClientRect();
      const fCenterX = fRect.left + fRect.width / 2;
      const fCenterY = fRect.top + fRect.height / 2;
      const fDist = Math.hypot(fCenterX - clickX, fCenterY - clickY);
      const fDelay = (fDist / Math.max(vw, vh)) * 0.35;

      dissolvingElements.push({
        el: bigFrame,
        delay: fDelay,
        driftX: 0,
        driftY: -10,
        driftZ: 30,
        rot: 0,
        dissolved: false,
        origOpacity: bigFrame.style.opacity,
        origTransform: bigFrame.style.transform,
        origFilter: bigFrame.style.filter,
        origTransition: bigFrame.style.transition,
      });

      // Sample along the 4 borders of the big glass layout square
      const borderStep = 10;
      // Top & Bottom borders
      for (let px = fRect.left; px <= fRect.right; px += borderStep) {
        // Top edge
        const distTop = Math.hypot(px - clickX, fRect.top - clickY);
        const targetTop = getReconstructTarget(particles.length);
        particles.push({
          origX: px,
          origY: fRect.top,
          x: px,
          y: fRect.top,
          z: (Math.random() - 0.5) * 30,
          vx: (Math.random() - 0.5) * 4,
          vy: -2.5 - Math.random() * 4.0,
          vz: (Math.random() - 0.5) * 15,
          targetX: targetTop.x,
          targetY: targetTop.y,
          targetZ: targetTop.z,
          rotX: Math.random() * Math.PI,
          rotY: Math.random() * Math.PI,
          rotZ: Math.random() * Math.PI,
          vRotX: 0.1,
          vRotY: 0.1,
          vRotZ: 0.1,
          size: 1.8 + Math.random() * 2.2,
          r: 200,
          g: 230,
          b: 255,
          baseAlpha: 0.95,
          alpha: 1,
          elemType: 'frame',
          shape: 'shard',
          waveDelay: (distTop / Math.max(vw, vh)) * 0.38,
          active: false,
        });

        // Bottom edge
        const distBot = Math.hypot(px - clickX, fRect.bottom - clickY);
        const targetBot = getReconstructTarget(particles.length);
        particles.push({
          origX: px,
          origY: fRect.bottom,
          x: px,
          y: fRect.bottom,
          z: (Math.random() - 0.5) * 30,
          vx: (Math.random() - 0.5) * 4,
          vy: -1.5 - Math.random() * 3.0,
          vz: (Math.random() - 0.5) * 15,
          targetX: targetBot.x,
          targetY: targetBot.y,
          targetZ: targetBot.z,
          rotX: Math.random() * Math.PI,
          rotY: Math.random() * Math.PI,
          rotZ: Math.random() * Math.PI,
          vRotX: 0.1,
          vRotY: 0.1,
          vRotZ: 0.1,
          size: 1.8 + Math.random() * 2.2,
          r: 200,
          g: 230,
          b: 255,
          baseAlpha: 0.95,
          alpha: 1,
          elemType: 'frame',
          shape: 'shard',
          waveDelay: (distBot / Math.max(vw, vh)) * 0.38,
          active: false,
        });
      }

      // Left & Right borders
      for (let py = fRect.top; py <= fRect.bottom; py += borderStep) {
        // Left edge
        const distL = Math.hypot(fRect.left - clickX, py - clickY);
        const targetL = getReconstructTarget(particles.length);
        particles.push({
          origX: fRect.left,
          origY: py,
          x: fRect.left,
          y: py,
          z: (Math.random() - 0.5) * 30,
          vx: -2.0 - Math.random() * 3.5,
          vy: -1.5 - Math.random() * 2.5,
          vz: (Math.random() - 0.5) * 15,
          targetX: targetL.x,
          targetY: targetL.y,
          targetZ: targetL.z,
          rotX: Math.random() * Math.PI,
          rotY: Math.random() * Math.PI,
          rotZ: Math.random() * Math.PI,
          vRotX: 0.1,
          vRotY: 0.1,
          vRotZ: 0.1,
          size: 1.8 + Math.random() * 2.2,
          r: 200,
          g: 230,
          b: 255,
          baseAlpha: 0.95,
          alpha: 1,
          elemType: 'frame',
          shape: 'shard',
          waveDelay: (distL / Math.max(vw, vh)) * 0.38,
          active: false,
        });

        // Right edge
        const distR = Math.hypot(fRect.right - clickX, py - clickY);
        const targetR = getReconstructTarget(particles.length);
        particles.push({
          origX: fRect.right,
          origY: py,
          x: fRect.right,
          y: py,
          z: (Math.random() - 0.5) * 30,
          vx: 2.0 + Math.random() * 3.5,
          vy: -1.5 - Math.random() * 2.5,
          vz: (Math.random() - 0.5) * 15,
          targetX: targetR.x,
          targetY: targetR.y,
          targetZ: targetR.z,
          rotX: Math.random() * Math.PI,
          rotY: Math.random() * Math.PI,
          rotZ: Math.random() * Math.PI,
          vRotX: 0.1,
          vRotY: 0.1,
          vRotZ: 0.1,
          size: 1.8 + Math.random() * 2.2,
          r: 200,
          g: 230,
          b: 255,
          baseAlpha: 0.95,
          alpha: 1,
          elemType: 'frame',
          shape: 'shard',
          waveDelay: (distR / Math.max(vw, vh)) * 0.38,
          active: false,
        });
      }
    }

    if (svgMask) {
      dissolvingElements.push({
        el: svgMask,
        delay: 0.25,
        driftX: 0,
        driftY: 0,
        driftZ: 0,
        rot: 0,
        dissolved: false,
        origOpacity: svgMask.style.opacity,
        origTransform: svgMask.style.transform,
        origFilter: svgMask.style.filter,
        origTransition: svgMask.style.transition,
      });
    }

    // 2. Query ALL visible DOM components, text, buttons, and cards
    const querySelectors = [
      'h1', 'h2', 'h3', 'p', 'span', 'button', 'a',
      '.glass-level-3', '.glass-level-2', '.glass-level-1',
      '[class*="rounded-2xl"]', '[class*="rounded-[2.5rem]"]',
      'header', 'svg', '[data-cursor-hover]', 'input', 'section', 'img'
    ];

    const elements = document.querySelectorAll(querySelectors.join(','));
    let pIndex = particles.length;

    elements.forEach((el) => {
      if (!(el instanceof HTMLElement) && !(el instanceof SVGElement)) return;
      if (el.id === 'landing-glass-frame' || el.id === 'landing-svg-mask') return;

      const rect = el.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > vh || rect.right < 0 || rect.left > vw) return;
      if (rect.width < 8 || rect.height < 8) return;

      const style = window.getComputedStyle(el);
      const isText = el.tagName === 'H1' || el.tagName === 'H2' || el.tagName === 'H3' || el.tagName === 'P' || el.tagName === 'SPAN';
      const isButton = el.tagName === 'BUTTON' || el.tagName === 'A' || el.id?.includes('cta') || el.id?.includes('btn');
      const isCard = el.className?.toString().includes('glass') || el.className?.toString().includes('card') || rect.width > 200;

      const elCenterX = rect.left + rect.width / 2;
      const elCenterY = rect.top + rect.height / 2;
      const elDist = Math.hypot(elCenterX - clickX, elCenterY - clickY);
      const elDelay = (elDist / Math.max(vw, vh)) * 0.40;

      const elAngle = Math.atan2(elCenterY - clickY, elCenterX - clickX);
      const driftDist = 25 + Math.random() * 40;

      dissolvingElements.push({
        el: el as HTMLElement,
        delay: elDelay,
        driftX: Math.cos(elAngle) * driftDist,
        driftY: Math.sin(elAngle) * driftDist - 15,
        driftZ: (Math.random() - 0.5) * 50,
        rot: (Math.random() - 0.5) * 12,
        dissolved: false,
        origOpacity: el.style.opacity,
        origTransform: el.style.transform,
        origFilter: el.style.filter,
        origTransition: el.style.transition,
      });

      let r = 245, g = 247, b = 250;
      if (isButton || el.className?.toString().includes('sky') || style.color.includes('56') || style.borderColor.includes('56')) {
        r = 56; g = 189; b = 248;
      } else if (style.color.includes('96') || style.background.includes('60A5FA')) {
        r = 96; g = 165; b = 250;
      } else if (style.color.includes('34') || style.color.includes('52')) {
        r = 52; g = 211; b = 153;
      } else if (isCard) {
        r = 180; g = 205; b = 230;
      }

      let step = 10;
      if (isText) step = 6;
      if (isButton) step = 4;
      if (rect.width * rect.height > 200000) step = 26;

      for (let py = rect.top; py <= rect.bottom; py += step) {
        for (let px = rect.left; px <= rect.right; px += step) {
          const jx = px + (Math.random() - 0.5) * (step * 0.85);
          const jy = py + (Math.random() - 0.5) * (step * 0.85);

          if (jx < 0 || jx > vw || jy < 0 || jy > vh) continue;

          const dist = Math.hypot(jx - clickX, jy - clickY);
          const waveDelay = (dist / Math.max(vw, vh)) * 0.38;

          const angle = Math.atan2(jy - clickY, jx - clickX) + (Math.random() - 0.5) * 0.85;
          const speed = 3.8 + Math.random() * 7.5;
          const zSpeed = (Math.random() - 0.45) * 16;

          const target = getReconstructTarget(pIndex);

          particles.push({
            origX: jx,
            origY: jy,
            x: jx,
            y: jy,
            z: (Math.random() - 0.5) * 40,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed - (1.5 + Math.random() * 2.2),
            vz: zSpeed,
            targetX: target.x,
            targetY: target.y,
            targetZ: target.z,
            rotX: Math.random() * Math.PI * 2,
            rotY: Math.random() * Math.PI * 2,
            rotZ: Math.random() * Math.PI * 2,
            vRotX: (Math.random() - 0.5) * 0.22,
            vRotY: (Math.random() - 0.5) * 0.22,
            vRotZ: (Math.random() - 0.5) * 0.22,
            size: isText ? 1.4 + Math.random() * 1.8 : isButton ? 2.0 + Math.random() * 2.2 : 1.6 + Math.random() * 2.6,
            r,
            g,
            b,
            baseAlpha: 0.90 + Math.random() * 0.10,
            alpha: 1,
            elemType: isText ? 'text' : isButton ? 'button' : isCard ? 'card' : 'icon',
            shape: isText ? 'dot' : isButton ? 'rect' : 'shard',
            waveDelay,
            active: false,
          });

          pIndex++;
        }
      }
    });

    // 3. Ambient 3D glowing cosmic dust
    for (let i = 0; i < 350; i++) {
      const ax = Math.random() * vw;
      const ay = Math.random() * vh;
      const dist = Math.hypot(ax - clickX, ay - clickY);
      const target = getReconstructTarget(pIndex++);

      particles.push({
        origX: ax,
        origY: ay,
        x: ax,
        y: ay,
        z: -150 + Math.random() * 500,
        vx: (Math.random() - 0.5) * 3,
        vy: (Math.random() - 0.5) * 3 - 0.6,
        vz: (Math.random() - 0.5) * 8,
        targetX: target.x,
        targetY: target.y,
        targetZ: target.z,
        rotX: Math.random() * Math.PI,
        rotY: Math.random() * Math.PI,
        rotZ: Math.random() * Math.PI,
        vRotX: 0.05,
        vRotY: 0.05,
        vRotZ: 0.05,
        size: 1.2 + Math.random() * 1.8,
        r: 56,
        g: 189,
        b: 248,
        baseAlpha: 0.5 + Math.random() * 0.4,
        alpha: 0.7,
        elemType: 'ambient',
        shape: 'dot',
        waveDelay: (dist / Math.max(vw, vh)) * 0.35,
        active: false,
      });
    }

    dissolvingElementsRef.current = dissolvingElements;
    return particles;
  };

  // The Animation Engine
  const startDisintegration = useCallback((clickX?: number, clickY?: number) => {
    if (isTransitioningRef.current) return;
    isTransitioningRef.current = true;
    setIsRunning(true);
    playCinematicAudio();

    const canvas = canvasRef.current;
    if (!canvas) {
      router.push(targetHref);
      return;
    }

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) {
      router.push(targetHref);
      return;
    }

    const vw = window.innerWidth;
    const vh = window.innerHeight;
    canvas.width = vw;
    canvas.height = vh;

    const originX = clickX ?? vw / 2;
    const originY = clickY ?? vh / 2;

    const particles = samplePageElements(originX, originY);
    const DURATION = 1600;
    const startTime = performance.now();

    const fov = 650;
    const cameraCenter = { x: vw / 2, y: vh / 2 };

    let hasNavigated = false;

    const render = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / DURATION);

      ctx.clearRect(0, 0, vw, vh);

      const p1 = Math.min(1, progress / 0.38);
      const p3 = Math.max(0, Math.min(1, (progress - 0.60) / 0.30));
      const p4 = Math.max(0, Math.min(1, (progress - 0.90) / 0.10));

      // AVENGERS DUST DISSOLUTION FOR ACTUAL DOM ELEMENTS + BIG GLASS FRAME:
      const dissolvingList = dissolvingElementsRef.current;
      for (let d = 0; d < dissolvingList.length; d++) {
        const item = dissolvingList[d];
        if (!item.dissolved && progress >= item.delay) {
          item.dissolved = true;
          item.el.style.transition = 'opacity 0.40s cubic-bezier(0.4, 0, 0.2, 1), transform 0.50s cubic-bezier(0.4, 0, 0.2, 1), filter 0.35s ease-out';
          item.el.style.filter = 'blur(6px) brightness(1.8) drop-shadow(0 0 12px rgba(56, 189, 248, 0.9))';
          item.el.style.opacity = '0';
          item.el.style.transform = `translate3d(${item.driftX}px, ${item.driftY}px, ${item.driftZ}px) scale(0.92) rotate(${item.rot}deg)`;
        }
      }

      // Camera Z movement
      let cameraZ = 0;
      if (progress > 0.30 && progress <= 0.75) {
        cameraZ = Math.sin((progress - 0.30) / 0.45 * Math.PI) * 200;
      }

      // Shockwave cyan glowing ring
      const ringRadius = p1 * Math.max(vw, vh) * 1.1;
      if (p1 > 0.01 && p1 < 1 && ringRadius > 5) {
        const innerR = Math.max(0.1, ringRadius - 70);
        const outerR = Math.max(innerR + 1, ringRadius);
        try {
          const ringGrad = ctx.createRadialGradient(originX, originY, innerR, originX, originY, outerR);
          ringGrad.addColorStop(0, 'rgba(56, 189, 248, 0)');
          ringGrad.addColorStop(0.5, `rgba(56, 189, 248, ${(1 - p1) * 0.35})`);
          ringGrad.addColorStop(1, 'rgba(56, 189, 248, 0)');
          ctx.fillStyle = ringGrad;
          ctx.fillRect(0, 0, vw, vh);
        } catch {
          // Safeguard
        }
      }

      // Luminous crystallization glow during convergence (Phase 3)
      if (p3 > 0.05) {
        const glowAlpha = Math.sin(p3 * Math.PI) * 0.25;
        const grad = ctx.createRadialGradient(vw / 2, vh * 0.45, 50, vw / 2, vh * 0.45, Math.max(vw, vh) * 0.6);
        grad.addColorStop(0, `rgba(56, 189, 248, ${glowAlpha})`);
        grad.addColorStop(0.5, `rgba(96, 165, 250, ${glowAlpha * 0.5})`);
        grad.addColorStop(1, 'rgba(7, 9, 13, 0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, vw, vh);
      }

      // Update & Render all Particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (!p.active && progress >= p.waveDelay) {
          p.active = true;
        }

        if (p.active) {
          if (progress < 0.60) {
            p.x += p.vx;
            p.y += p.vy;
            p.z += p.vz;

            p.vx *= 0.96;
            p.vy *= 0.96;
            p.vz *= 0.96;

            p.x += Math.sin(p.y * 0.02 + elapsed * 0.003) * 0.6;
            p.y += Math.cos(p.x * 0.02 + elapsed * 0.003) * 0.6;

            p.rotX += p.vRotX;
            p.rotY += p.vRotY;
            p.rotZ += p.vRotZ;
          } else {
            const easeT = Math.pow(p3, 2.2);
            p.x = p.x + (p.targetX - p.x) * (0.10 + easeT * 0.20);
            p.y = p.y + (p.targetY - p.y) * (0.10 + easeT * 0.20);
            p.z = p.z + (p.targetZ - p.z) * (0.10 + easeT * 0.20);

            p.rotX *= 0.90;
            p.rotY *= 0.90;
            p.rotZ *= 0.90;
          }

          const effectiveZ = p.z - cameraZ;
          const scale = fov / (fov + effectiveZ);

          if (scale > 0 && effectiveZ > -fov + 20) {
            const projX = (p.x - cameraCenter.x) * scale + cameraCenter.x;
            const projY = (p.y - cameraCenter.y) * scale + cameraCenter.y;
            const projSize = Math.max(0.6, p.size * scale);

            let alpha = p.baseAlpha;
            if (p3 > 0) {
              alpha = Math.min(1, p.baseAlpha + p3 * 0.4);
            }
            if (effectiveZ < 0) {
              alpha *= Math.max(0.1, 1 + effectiveZ / 300);
            }

            ctx.save();
            ctx.translate(projX, projY);
            ctx.rotate(p.rotZ);

            if (p.shape === 'rect') {
              ctx.fillStyle = `rgba(${p.r}, ${p.g}, ${p.b}, ${alpha})`;
              ctx.fillRect(-projSize / 2, -projSize / 2, projSize * 1.4, projSize * 0.8);
            } else if (p.shape === 'shard') {
              ctx.fillStyle = `rgba(${p.r}, ${p.g}, ${p.b}, ${alpha})`;
              ctx.beginPath();
              ctx.moveTo(0, -projSize);
              ctx.lineTo(projSize * 0.8, projSize * 0.6);
              ctx.lineTo(-projSize * 0.8, projSize * 0.6);
              ctx.closePath();
              ctx.fill();
            } else {
              ctx.fillStyle = `rgba(${p.r}, ${p.g}, ${p.b}, ${alpha})`;
              ctx.beginPath();
              ctx.arc(0, 0, projSize, 0, Math.PI * 2);
              ctx.fill();

              if (projSize > 1.8 && (p.elemType === 'button' || p.elemType === 'text' || p.elemType === 'frame')) {
                ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.75})`;
                ctx.beginPath();
                ctx.arc(0, 0, projSize * 0.45, 0, Math.PI * 2);
                ctx.fill();
              }
            }

            ctx.restore();
          }
        }
      }

      // Smooth trigger navigation handoff at 85% progress
      if (progress >= 0.85 && !hasNavigated) {
        hasNavigated = true;
        router.push(targetHref);
      }

      if (progress < 1) {
        animFrameRef.current = requestAnimationFrame(render);
      }
    };

    animFrameRef.current = requestAnimationFrame(render);
  }, [router, targetHref]);

  // Expose trigger callback directly to triggerRef and Custom Event listener
  useEffect(() => {
    if (triggerRef) {
      triggerRef.current = (e?: React.MouseEvent | MouseEvent) => {
        const cx = e ? e.clientX : window.innerWidth / 2;
        const cy = e ? e.clientY : window.innerHeight / 2;
        startDisintegration(cx, cy);
      };
    }

    const handleCustomEvent = (e: Event) => {
      const custom = e as CustomEvent<{ x: number; y: number }>;
      startDisintegration(custom.detail?.x, custom.detail?.y);
    };

    window.addEventListener('trigger-disintegration', handleCustomEvent);
    return () => {
      window.removeEventListener('trigger-disintegration', handleCustomEvent);
    };
  }, [triggerRef, startDisintegration]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      dissolvingElementsRef.current.forEach((item) => {
        item.el.style.opacity = item.origOpacity;
        item.el.style.transform = item.origTransform;
        item.el.style.filter = item.origFilter;
        item.el.style.transition = item.origTransition;
      });
    };
  }, []);

  return (
    <div
      className="fixed inset-0 z-[9999] pointer-events-none overflow-hidden"
      style={{ display: isRunning ? 'block' : 'none' }}
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full block bg-transparent"
      />
    </div>
  );
};
