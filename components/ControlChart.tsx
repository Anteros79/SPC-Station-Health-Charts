
import React, { useMemo } from 'react';
import type { AugmentedData } from '../types';
import { ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line, ReferenceLine, ReferenceArea } from 'recharts';

interface ControlChartProps {
    data: AugmentedData;
    title: string;
}

const romanize = (num: number): string => {
    const lookup: { [key: string]: number } = {M:1000,CM:900,D:500,CD:400,C:100,XC:90,L:50,XL:40,X:10,IX:9,V:5,IV:4,I:1};
    let roman = '';
    for (let i in lookup ) {
        while ( num >= lookup[i] ) {
            roman += i;
            num -= lookup[i];
        }
    }
    return roman;
}

const CustomTooltip = React.memo<any>(({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-gray-700 text-white p-3 rounded-md border border-gray-600 shadow-lg">
        <p className="font-bold">{`Date: ${new Date(data.date).toLocaleDateString()}`}</p>
        <p style={{ color: '#8884d8' }}>{`Value: ${data.value.toFixed(2)}`}</p>
        <p style={{ color: '#82ca9d' }}>{`CL: ${data.cl?.toFixed(2)}`}</p>
        <p style={{ color: '#ff7300' }}>{`UCL: ${data.ucl?.toFixed(2)}`}</p>
        <p style={{ color: '#ff7300' }}>{`LCL: ${data.lcl?.toFixed(2)}`}</p>
      </div>
    );
  }
  return null;
});

const ControlChart: React.FC<ControlChartProps> = React.memo(({ data, title }) => {
    const { points, phases } = data;
    
    if (!points || points.length === 0) {
        return <div className="text-center text-gray-500 p-4">No data available for {title}</div>;
    }

    const yDomain = useMemo(() => {
        if (!points || points.length === 0) return [0, 100];
        
        return [
            Math.min(...points.map(p => Math.min(p.value, p.lcl ?? p.value))) * 0.95,
            Math.max(...points.map(p => Math.max(p.value, p.ucl ?? p.value))) * 1.05
        ];
    }, [points]);

    return (
        <div className="h-96 w-full">
            <h3 className="text-xl font-semibold text-center mb-4 text-gray-200">{title}</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={points} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
                    <XAxis 
                        dataKey="date" 
                        tickFormatter={(tick) => new Date(tick).toLocaleDateString()} 
                        stroke="#A0AEC0"
                        minTickGap={40}
                    />
                    <YAxis stroke="#A0AEC0" domain={yDomain} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />

                    {phases.map((phase, index) => (
                        index > 0 && <ReferenceLine key={`phase-line-${index}`} x={points[phase.startIndex].date} stroke="white" strokeDasharray="2 2" />
                    ))}
                    
                    {phases.map((phase, index) => (
                         <ReferenceArea 
                             key={`phase-label-${index}`}
                             x1={points[phase.startIndex].date} 
                             x2={points[phase.endIndex].date} 
                             y1={yDomain[1]} // Position at the top
                             y2={yDomain[1]} // Position at the top
                             ifOverflow="visible"
                             label={{ value: `Phase ${romanize(index + 1)}`, position: 'insideTop', fill: '#E2E8F0', fontSize: 14, dy: -5 }}
                         />
                    ))}
                    
                    <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2} dot={false} name="Value" />
                    <Line type="stepAfter" dataKey="cl" stroke="#4ade80" strokeWidth={2} dot={false} name="Center Line (CL)" />
                    <Line type="stepAfter" dataKey="ucl" stroke="#fb923c" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Upper Control Limit (UCL)" />
                    <Line type="stepAfter" dataKey="lcl" stroke="#fb923c" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Lower Control Limit (LCL)" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
});

export default ControlChart;
