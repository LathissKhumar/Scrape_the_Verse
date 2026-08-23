'use client';

import React, { useEffect, useRef } from 'react';

interface Node {
  x: number;
  y: number;
  baseVx: number;
  baseVy: number;
  vx: number;
  vy: number;
  radius: number;
  layer: number; // 0 = far, 1 = mid, 2 = near
  baseAlpha: number;
  colorType: 'white' | 'cyan' | 'blue';
  phase: number;
  phaseSpeed: number;
}

interface Pulse {
  fromIdx: number;
  toIdx: number;
  progress: number;
  speed: number;
  colorType: 'cyan' | 'white';
}

interface NeuralWebBackgroundProps {
  className?: string;
  intensity?: 'subtle' | 'medium' | 'vibrant';
  interactive?: boolean;
}

export const NeuralWebBackground: React.FC<NeuralWebBackgroundProps> = ({
  className = '',
  intensity = 'subtle',
  interactive = true,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    let animationFrameId: number;
    let width = 0;
    let height = 0;
    let dpr = 1;

    let nodes: Node[] = [];
    let pulses: Pulse[] = [];
    let nextPulseSpawn = 60; // frames until next pulse attempt

    // Smooth interpolated mouse position
    const mouse = { x: -9999, y: -9999, targetX: -9999, targetY: -9999, active: false };

    // Multipliers based on intensity prop
    const intensityMultiplier = intensity === 'vibrant' ? 1.4 : intensity === 'medium' ? 1.15 : 1.0;

    // Resize and initialize node matrix
    const handleResize = () => {
      if (!canvas || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      width = rect.width || window.innerWidth;
      height = rect.height || window.innerHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.scale(dpr, dpr);

      initNodes();
    };

    const initNodes = () => {
      nodes = [];
      pulses = [];

      // Calculate node count proportionally based on screen area
      let targetNodeCount = 80;
      if (width >= 1600) targetNodeCount = 100;
      else if (width >= 1200) targetNodeCount = 85;
      else if (width >= 768) targetNodeCount = 65;
      else targetNodeCount = 38; // Mobile

      for (let i = 0; i < targetNodeCount; i++) {
        // Multi-depth layer distribution: 50% Far (0), 35% Mid (1), 15% Near (2)
        const rand = Math.random();
        let layer = 0;
        let radius = 1.0;
        let speed = 0.12;
        let baseAlpha = 0.22;
        let colorType: 'white' | 'cyan' | 'blue' = 'white';

        if (rand < 0.50) {
          // Far layer (tiny, faint, very slow drift)
          layer = 0;
          radius = 0.75 + Math.random() * 0.5;
          speed = 0.06 + Math.random() * 0.08;
          baseAlpha = 0.16 + Math.random() * 0.10;
          colorType = 'white';
        } else if (rand < 0.85) {
          // Middle layer (moderate size and opacity)
          layer = 1;
          radius = 1.2 + Math.random() * 0.6;
          speed = 0.12 + Math.random() * 0.14;
          baseAlpha = 0.28 + Math.random() * 0.16;
          colorType = Math.random() < 0.3 ? 'cyan' : 'white';
        } else {
          // Near layer (spatial accent points, soft glow)
          layer = 2;
          radius = 1.8 + Math.random() * 0.8;
          speed = 0.18 + Math.random() * 0.20;
          baseAlpha = 0.45 + Math.random() * 0.22;
          colorType = Math.random() < 0.6 ? 'cyan' : 'blue';
        }

        const angle = Math.random() * Math.PI * 2;
        const vx = Math.cos(angle) * speed;
        const vy = Math.sin(angle) * speed;

        nodes.push({
          x: Math.random() * width,
          y: Math.random() * height,
          baseVx: vx,
          baseVy: vy,
          vx: vx,
          vy: vy,
          radius,
          layer,
          baseAlpha: baseAlpha * intensityMultiplier,
          colorType,
          phase: Math.random() * Math.PI * 2,
          phaseSpeed: 0.01 + Math.random() * 0.015,
        });
      }
    };

    // Mouse handlers
    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = canvas.getBoundingClientRect();
      mouse.targetX = e.clientX - rect.left;
      mouse.targetY = e.clientY - rect.top;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
      mouse.targetX = -9999;
      mouse.targetY = -9999;
    };

    window.addEventListener('resize', handleResize);
    if (interactive) {
      window.addEventListener('mousemove', handleMouseMove, { passive: true });
      document.addEventListener('mouseleave', handleMouseLeave);
    }

    // Visibility API to pause rendering when tab is unfocused
    let isTabVisible = true;
    const handleVisibilityChange = () => {
      isTabVisible = !document.hidden;
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    handleResize();

    // Main animation loop
    const render = () => {
      if (!isTabVisible) {
        animationFrameId = requestAnimationFrame(render);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Smooth mouse lerp
      if (mouse.active) {
        mouse.x += (mouse.targetX - mouse.x) * 0.06;
        mouse.y += (mouse.targetY - mouse.y) * 0.06;
      } else {
        mouse.x = -9999;
        mouse.y = -9999;
      }

      const activeConnections: { i: number; j: number; dist: number }[] = [];

      // 1. UPDATE NODE POSITIONS & GENTLE ORGANIC DRIFT
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];

        // Smooth subtle sine-wave drift modulation
        n.phase += n.phaseSpeed;
        const driftX = Math.sin(n.phase) * 0.04;
        const driftY = Math.cos(n.phase * 0.8) * 0.04;

        // Subtle gentle mouse displacement (whisper light)
        if (mouse.active) {
          const dx = n.x - mouse.x;
          const dy = n.y - mouse.y;
          const distToMouse = Math.sqrt(dx * dx + dy * dy);
          const mouseRadius = 160;

          if (distToMouse < mouseRadius && distToMouse > 0) {
            const force = (1 - distToMouse / mouseRadius) * 0.12;
            n.vx += (dx / distToMouse) * force;
            n.vy += (dy / distToMouse) * force;
          }
        }

        // Apply velocities with damping back toward base speed
        n.vx = n.vx * 0.96 + n.baseVx * 0.04;
        n.vy = n.vy * 0.96 + n.baseVy * 0.04;

        n.x += n.vx + driftX;
        n.y += n.vy + driftY;

        // Soft screen edge wraparound with margin
        const margin = 40;
        if (n.x < -margin) n.x = width + margin;
        else if (n.x > width + margin) n.x = -margin;
        if (n.y < -margin) n.y = height + margin;
        else if (n.y > height + margin) n.y = -margin;
      }

      // 2. DRAW CONNECTION LINES WITH DISTANCE & DEPTH FADING
      const maxDistanceByLayer = [95, 135, 170]; // Far, Mid, Near max line lengths

      for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];

        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];

          // Max distance allowed between these two nodes
          const maxDist = Math.max(maxDistanceByLayer[n1.layer], maxDistanceByLayer[n2.layer]);
          const dx = n1.x - n2.x;
          const dy = n1.y - n2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDist) {
            const distRatio = 1 - dist / maxDist; // 1.0 (close) -> 0.0 (far)

            // Base opacity determined by average node layer and distance
            const avgLayer = (n1.layer + n2.layer) / 2;
            let lineMaxAlpha = 0.07;
            if (avgLayer > 1.2) lineMaxAlpha = 0.18;
            else if (avgLayer > 0.6) lineMaxAlpha = 0.12;

            let alpha = distRatio * lineMaxAlpha * intensityMultiplier;

            // Extra subtle highlight if connection is near mouse cursor
            if (mouse.active) {
              const midX = (n1.x + n2.x) / 2;
              const midY = (n1.y + n2.y) / 2;
              const dMouse = Math.sqrt((midX - mouse.x) ** 2 + (midY - mouse.y) ** 2);
              if (dMouse < 140) {
                const mouseBoost = (1 - dMouse / 140) * 0.08;
                alpha += mouseBoost;
              }
            }

            if (alpha > 0.015) {
              ctx.beginPath();
              ctx.moveTo(n1.x, n1.y);
              ctx.lineTo(n2.x, n2.y);

              // Use subtle cyan line for near/mid layer nodes, white for others
              if (n1.colorType === 'cyan' || n2.colorType === 'cyan') {
                ctx.strokeStyle = `rgba(56, 189, 248, ${Math.min(0.28, alpha * 1.15).toFixed(3)})`;
              } else if (n1.colorType === 'blue' || n2.colorType === 'blue') {
                ctx.strokeStyle = `rgba(96, 165, 250, ${Math.min(0.25, alpha).toFixed(3)})`;
              } else {
                ctx.strokeStyle = `rgba(255, 255, 255, ${Math.min(0.22, alpha).toFixed(3)})`;
              }

              ctx.lineWidth = n1.layer === 2 || n2.layer === 2 ? 0.9 : 0.65;
              ctx.stroke();

              // Record valid connection for potential pulse transmission
              if (distRatio > 0.3) {
                activeConnections.push({ i, j, dist });
              }
            }
          }
        }
      }

      // 3. SPAWN & DRAW NEURAL PULSE PACKETS (Infrequent subtle data flow pulses)
      nextPulseSpawn--;
      if (nextPulseSpawn <= 0 && activeConnections.length > 0 && pulses.length < 5) {
        // Pick a random active connection
        const randomConn = activeConnections[Math.floor(Math.random() * activeConnections.length)];
        pulses.push({
          fromIdx: randomConn.i,
          toIdx: randomConn.j,
          progress: 0,
          speed: 0.009 + Math.random() * 0.012, // Slow, elegant pulse speed
          colorType: Math.random() < 0.75 ? 'cyan' : 'white',
        });
        nextPulseSpawn = 120 + Math.floor(Math.random() * 160); // Next pulse in ~2-4.5 seconds
      }

      // Update and draw active pulses
      for (let pIdx = pulses.length - 1; pIdx >= 0; pIdx--) {
        const pulse = pulses[pIdx];
        pulse.progress += pulse.speed;

        if (pulse.progress >= 1.0) {
          pulses.splice(pIdx, 1);
          continue;
        }

        const n1 = nodes[pulse.fromIdx];
        const n2 = nodes[pulse.toIdx];
        if (!n1 || !n2) {
          pulses.splice(pIdx, 1);
          continue;
        }

        const currentX = n1.x + (n2.x - n1.x) * pulse.progress;
        const currentY = n1.y + (n2.y - n1.y) * pulse.progress;

        // Pulse alpha bell curve (fades in, peaks at center, fades out)
        const pulseAlpha = Math.sin(pulse.progress * Math.PI) * (pulse.colorType === 'cyan' ? 0.75 : 0.6);

        // Draw glowing pulse dot
        ctx.beginPath();
        ctx.arc(currentX, currentY, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = pulse.colorType === 'cyan' 
          ? `rgba(56, 189, 248, ${pulseAlpha.toFixed(3)})`
          : `rgba(255, 255, 255, ${pulseAlpha.toFixed(3)})`;
        ctx.shadowColor = 'rgba(56, 189, 248, 0.8)';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0; // reset shadow
      }

      // 4. DRAW NODES WITH SPATIAL DEPTH & RADIAL GLOWS
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];

        // Soft radial glow for near and mid layers
        if (n.layer >= 1) {
          const glowRadius = n.radius * (n.layer === 2 ? 3.5 : 2.5);
          const glowGrad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, glowRadius);
          
          if (n.colorType === 'cyan') {
            glowGrad.addColorStop(0, `rgba(56, 189, 248, ${(n.baseAlpha * 0.45).toFixed(3)})`);
            glowGrad.addColorStop(1, 'rgba(56, 189, 248, 0)');
          } else if (n.colorType === 'blue') {
            glowGrad.addColorStop(0, `rgba(96, 165, 250, ${(n.baseAlpha * 0.40).toFixed(3)})`);
            glowGrad.addColorStop(1, 'rgba(96, 165, 250, 0)');
          } else {
            glowGrad.addColorStop(0, `rgba(255, 255, 255, ${(n.baseAlpha * 0.35).toFixed(3)})`);
            glowGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
          }

          ctx.beginPath();
          ctx.arc(n.x, n.y, glowRadius, 0, Math.PI * 2);
          ctx.fillStyle = glowGrad;
          ctx.fill();
        }

        // Draw solid node center point
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);

        if (n.colorType === 'cyan') {
          ctx.fillStyle = `rgba(186, 230, 253, ${Math.min(0.85, n.baseAlpha * 1.4).toFixed(3)})`;
        } else if (n.colorType === 'blue') {
          ctx.fillStyle = `rgba(191, 219, 254, ${Math.min(0.80, n.baseAlpha * 1.3).toFixed(3)})`;
        } else {
          ctx.fillStyle = `rgba(255, 255, 255, ${n.baseAlpha.toFixed(3)})`;
        }

        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (interactive) {
        window.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseleave', handleMouseLeave);
      }
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [intensity, interactive]);

  return (
    <div
      ref={containerRef}
      className={`fixed inset-0 z-0 pointer-events-none overflow-hidden bg-[#040711] ${className}`}
      aria-hidden="true"
    >
      {/* 1. SLOW-MOVING SPATIAL ATMOSPHERIC LIGHT FIELDS */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {/* Top-Center Ambient Cyan Atmospheric Nebula (Slow Breathing) */}
        <div className="absolute -top-[20%] left-1/2 -translate-x-1/2 w-[1200px] h-[750px] bg-[radial-gradient(ellipse_at_center,rgba(56,189,248,0.13)_0%,transparent_70%)] rounded-full blur-[140px] animate-pulse duration-[12000ms] pointer-events-none" />

        {/* Ambient Top-Left Azure Atmosphere Glow */}
        <div className="absolute top-[8%] -left-[12%] w-[800px] h-[800px] bg-[radial-gradient(circle,rgba(96,165,250,0.07)_0%,transparent_65%)] rounded-full blur-[160px] pointer-events-none" />

        {/* Ambient Mid-Right Soft Cyan Nebula */}
        <div className="absolute top-[35%] -right-[12%] w-[850px] h-[850px] bg-[radial-gradient(circle,rgba(56,189,248,0.07)_0%,transparent_65%)] rounded-full blur-[170px] pointer-events-none" />

        {/* Deep Horizon Indigo Atmosphere */}
        <div className="absolute -bottom-[25%] left-1/4 w-[1000px] h-[900px] bg-[radial-gradient(ellipse_at_center,rgba(129,140,248,0.06)_0%,transparent_70%)] rounded-full blur-[180px] pointer-events-none" />

        {/* Subtle Spatial Micro-Grid Texture */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.018)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.018)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_75%_65%_at_50%_0%,#000_70%,transparent_100%)] opacity-50 pointer-events-none" />
      </div>

      {/* 2. SPATIAL NEURAL SPIDER-WEB CANVAS */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />
    </div>
  );
};
export default NeuralWebBackground;
