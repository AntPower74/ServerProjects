import React, { useEffect } from "react";
import { Clock, CreditCard, Route, Bell, CalendarDays } from "lucide-react";

const ITEMS = [
  { text: "La tua rotazione turni", icon: CalendarDays, dir: "left" },
  { text: "Il tuo turno", icon: Clock, dir: "right" },
  { text: "Cartellino", icon: CreditCard, dir: "left" },
  { text: "Orario corse", icon: Route, dir: "right" },
  { text: "Avviso turno", icon: Bell, dir: "left" },
];

const STAGGER_MS = 260;
const FIRST_ITEM_DELAY = 700;
const ITEM_ANIM_MS = 720;
const OUTRO_BUFFER_MS = 400;
const TOTAL_DURATION_MS =
  FIRST_ITEM_DELAY + (ITEMS.length - 1) * STAGGER_MS + ITEM_ANIM_MS + OUTRO_BUFFER_MS;

export default function SmartTurnoHome({ onFinish }) {
  useEffect(() => {
    if (!onFinish) return;
    const timer = setTimeout(onFinish, TOTAL_DURATION_MS);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="st-root">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@500&display=swap');

        * { box-sizing: border-box; }

        .st-root {
          --st-bg: radial-gradient(ellipse 120% 80% at 50% -10%, #142a4d 0%, #0a1628 55%, #060d1a 100%);
          --st-text: #edeff4;
          --st-cyan: #3ddbd9;
          --st-orange: #f5a623;
          --st-cyan-rgb: 61, 219, 217;
          --st-orange-rgb: 245, 166, 35;

          min-height: 100vh;
          width: 100%;
          background: var(--st-bg);
          font-family: 'Inter', sans-serif;
          display: flex;
          justify-content: center;
          align-items: stretch;
          overflow: hidden;
          position: relative;
        }

        :root[data-theme="light"] .st-root {
          --st-bg: radial-gradient(ellipse 120% 80% at 50% -10%, #eef3fb 0%, #f7f9fc 55%, #ffffff 100%);
          --st-text: #17181c;
          --st-cyan: #0891b2;
          --st-orange: #c2660c;
          --st-cyan-rgb: 8, 145, 178;
          --st-orange-rgb: 194, 102, 12;
        }

        .st-frame {
          width: 100%;
          max-width: 420px;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          position: relative;
          padding: 0 28px;
        }

        /* subtle route line, drawn like a transit map path */
        .st-route {
          position: absolute;
          inset: 0;
          pointer-events: none;
          opacity: 0.35;
        }
        .st-route path {
          stroke: var(--st-cyan);
          stroke-width: 1.4;
          fill: none;
          stroke-dasharray: 6 10;
          animation: dash 26s linear infinite;
        }
        @keyframes dash {
          to { stroke-dashoffset: -400; }
        }

        .st-dot {
          fill: var(--st-orange);
          animation: pulse 2.6s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.4; r: 3.2; }
          50% { opacity: 1; r: 4.4; }
        }

        .st-top {
          padding-top: 56px;
          display: flex;
          flex-direction: column;
          gap: 6px;
          position: relative;
          z-index: 2;
        }

        .st-eyebrow {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 12px;
          letter-spacing: 0.28em;
          color: var(--st-cyan);
          text-transform: uppercase;
        }

        .st-wordmark {
          font-family: 'Space Grotesk', sans-serif;
          font-weight: 700;
          font-size: 40px;
          line-height: 1.05;
          color: var(--st-text);
          letter-spacing: -0.01em;
          opacity: 0;
          animation: wordmarkArrive 1000ms cubic-bezier(0.22, 1, 0.36, 1) 200ms forwards;
        }

        @keyframes wordmarkArrive {
          0%   { transform: translateX(-36px); opacity: 0; filter: blur(6px); }
          60%  { filter: blur(0px); }
          100% { transform: translateX(0); opacity: 1; filter: blur(0px); }
        }

        .st-wordmark span {
          color: var(--st-orange);
        }

        .st-board-wrap {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          z-index: 2;
          min-height: 220px;
        }

        .st-board {
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 22px;
          position: relative;
        }

        .st-item {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          width: 100%;
          position: relative;
          opacity: 0;
        }

        .st-item.enter-left {
          animation: slideFromLeft 720ms cubic-bezier(0.22, 1, 0.36, 1) both;
          animation-delay: var(--delay);
        }
        .st-item.enter-right {
          animation: slideFromRight 720ms cubic-bezier(0.22, 1, 0.36, 1) both;
          animation-delay: var(--delay);
        }

        /* scia luminosa dietro il testo mentre entra */
        .st-item::before {
          content: '';
          position: absolute;
          top: 50%;
          height: 2px;
          width: 70px;
          transform: translateY(-50%);
          filter: blur(2px);
          opacity: 0;
        }

        .st-item.enter-left::before {
          left: -20px;
          background: linear-gradient(90deg, transparent, rgba(var(--st-orange-rgb), 0.7));
          animation: trailLeft 720ms cubic-bezier(0.22, 1, 0.36, 1) both;
          animation-delay: var(--delay);
        }
        .st-item.enter-right::before {
          right: -20px;
          background: linear-gradient(270deg, transparent, rgba(var(--st-cyan-rgb), 0.7));
          animation: trailRight 720ms cubic-bezier(0.22, 1, 0.36, 1) both;
          animation-delay: var(--delay);
        }

        @keyframes slideFromLeft {
          0%   { transform: translateX(-70px); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideFromRight {
          0%   { transform: translateX(70px); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }

        @keyframes trailLeft {
          0%   { opacity: 0; transform: translateY(-50%) translateX(-70px) scaleX(0.5); }
          35%  { opacity: 1; }
          100% { opacity: 0; transform: translateY(-50%) translateX(0) scaleX(1); }
        }
        @keyframes trailRight {
          0%   { opacity: 0; transform: translateY(-50%) translateX(70px) scaleX(0.5); }
          35%  { opacity: 1; }
          100% { opacity: 0; transform: translateY(-50%) translateX(0) scaleX(1); }
        }

        .st-icon-badge {
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          border-radius: 9px;
          background: rgba(var(--st-orange-rgb), 0.12);
          border: 1px solid rgba(var(--st-orange-rgb), 0.35);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .st-item-text {
          font-family: 'Space Grotesk', sans-serif;
          font-weight: 700;
          font-size: 21px;
          color: var(--st-text);
          line-height: 1.15;
          text-align: center;
        }
      `}</style>

      <div className="st-frame">
        <svg className="st-route" viewBox="0 0 420 900" preserveAspectRatio="none">
          <path d="M -20 120 C 100 180, 60 320, 200 340 S 380 460, 340 600 S 200 760, 260 900" />
          <circle className="st-dot" cx="200" cy="340" r="3.5" />
        </svg>

        <div className="st-top">
          <div className="st-eyebrow">Gestione turni, semplice</div>
          <div className="st-wordmark">
            Smart<span>Turno</span>
          </div>
        </div>

        <div className="st-board-wrap">
          <div className="st-board">
            {ITEMS.map((item, i) => {
              const Icon = item.icon;
              const delay = FIRST_ITEM_DELAY + i * STAGGER_MS;
              return (
                <div
                  key={item.text}
                  className={`st-item enter-${item.dir}`}
                  style={{ "--delay": `${delay}ms` }}
                >
                  <div className="st-icon-badge">
                    <Icon size={16} color="var(--st-orange)" strokeWidth={2.2} />
                  </div>
                  <div className="st-item-text">{item.text}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
