
import React from 'react';
import ControlChart from './ControlChart';
import type { ChartData } from '../types';

interface DashboardProps {
    chartData: ChartData | null;
    selectedStation: string;
    monitoredStations: string[];
    isLoading: boolean;
    error: string | null;
}

const LoadingSpinner: React.FC = () => (
    <div className="flex justify-center items-center h-64">
        <svg className="animate-spin -ml-1 mr-3 h-10 w-10 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span className="text-xl text-gray-400">Processing Data...</span>
    </div>
);

const MessageDisplay: React.FC<{ message: string, type: 'info' | 'error' }> = ({ message, type }) => {
    const colorClass = type === 'error' ? 'text-red-400 bg-red-900/50 border-red-500' : 'text-gray-400 bg-gray-800 border-gray-700';
    return (
        <div className={`text-center p-8 rounded-lg border ${colorClass}`}>
            <p className="text-lg">{message}</p>
        </div>
    );
};


const StationCharts: React.FC<{ station: string; data: ChartData[string] }> = React.memo(({ station, data }) => {
    const measures = Object.keys(data).sort();
    
    if (measures.length === 0) {
        return (
             <div className="bg-gray-800 rounded-lg p-4 my-4">
                <h2 className="text-2xl font-bold text-cyan-400 mb-4 border-b border-gray-700 pb-2">{station}</h2>
                <p className="text-gray-500">No measures found for this station.</p>
            </div>
        );
    }
    
    return (
        <div className="mb-12">
            <h2 className="text-3xl font-bold text-cyan-400 mb-6 border-b-2 border-cyan-500 pb-2">{station}</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {measures.map(measure => (
                    <div key={`${station}-${measure}`} className="bg-gray-800 p-4 rounded-xl shadow-lg">
                        <ControlChart data={data[measure]} title={measure} />
                    </div>
                ))}
            </div>
        </div>
    );
});

const Dashboard: React.FC<DashboardProps> = ({ chartData, selectedStation, monitoredStations, isLoading, error }) => {
    if (isLoading) return <LoadingSpinner />;
    if (error) return <MessageDisplay message={`Error: ${error}`} type="error" />;
    if (!chartData) return <MessageDisplay message="No data loaded. Please upload a CSV or load the demo data." type="info" />;

    const stationsToRender = selectedStation === 'All Stations'
        ? monitoredStations.filter(station => chartData[station])
        : [selectedStation];
    
    if (stationsToRender.length === 0 || !chartData[stationsToRender[0]]) {
         return <MessageDisplay message={`No data available for the selected station(s).`} type="info" />;
    }

    return (
        <div>
            {stationsToRender.map(station => (
                chartData[station] && <StationCharts key={station} station={station} data={chartData[station]} />
            ))}
        </div>
    );
};

export default Dashboard;
