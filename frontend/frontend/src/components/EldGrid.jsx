import React from 'react';

const EldGrid = ({ grid }) => {
  const { intervals, transitions } = grid;
  
  const ROW_HEIGHT = 40;
  const GRID_WIDTH = 800;
  const GRID_HEIGHT = ROW_HEIGHT * 4;

  const getRowY = (index) => index * ROW_HEIGHT + ROW_HEIGHT / 2;

  return (
    <div className="w-full overflow-x-auto bg-white p-4 rounded-xl border border-outline-variant shadow-sm">
      <div className="min-w-[850px] relative">
        {/* Labels */}
        <div className="absolute left-0 top-0 bottom-0 w-24 flex flex-col justify-between py-2 text-[10px] font-bold text-on-surface-variant uppercase tracking-tighter border-r border-outline-variant bg-surface-container-low/50">
          <div className="h-10 flex items-center px-2">Off Duty</div>
          <div className="h-10 flex items-center px-2">Sleeper</div>
          <div className="h-10 flex items-center px-2">Driving</div>
          <div className="h-10 flex items-center px-2">On Duty</div>
        </div>

        {/* Grid and SVG */}
        <div className="ml-24 h-[160px] relative border-b border-outline-variant">
          {/* Vertical Grid Lines (Hours) */}
          <div className="absolute inset-0 flex">
            {Array.from({ length: 25 }).map((_, i) => (
              <div 
                key={i} 
                className={`flex-grow border-l ${i % 6 === 0 ? 'border-outline' : 'border-outline-variant/30'}`}
              >
                <span className="absolute -top-5 -left-1 text-[9px] font-mono text-outline">{i}</span>
              </div>
            ))}
          </div>

          {/* Horizontal Grid Lines */}
          <div className="absolute inset-0 flex flex-col">
             {[0, 1, 2, 3].map(i => (
               <div key={i} className="flex-grow border-t border-outline-variant/30" />
             ))}
          </div>

          {/* Duty Line SVG */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Intervals */}
            {intervals.map((interval, i) => (
              <line
                key={`int-${i}`}
                x1={`${interval.x_start * 100}%`}
                y1={getRowY(interval.row_index)}
                x2={`${interval.x_end * 100}%`}
                y2={getRowY(interval.row_index)}
                stroke="#0058be"
                strokeWidth="3"
                strokeLinecap="round"
              />
            ))}
            
            {/* Transitions */}
            {transitions.map((transition, i) => {
              const fromRow = [0, 1, 2, 3].indexOf(
                {"off_duty": 0, "sleeper": 1, "driving": 2, "on_duty": 3}[transition.from_status]
              );
              const toRow = [0, 1, 2, 3].indexOf(
                {"off_duty": 0, "sleeper": 1, "driving": 2, "on_duty": 3}[transition.to_status]
              );
              return (
                <line
                  key={`trans-${i}`}
                  x1={`${transition.x_position * 100}%`}
                  y1={getRowY(fromRow)}
                  x2={`${transition.x_position * 100}%`}
                  y2={getRowY(toRow)}
                  stroke="#0058be"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
              );
            })}
          </svg>
        </div>
      </div>
    </div>
  );
};

export default EldGrid;
