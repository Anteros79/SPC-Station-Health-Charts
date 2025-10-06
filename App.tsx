import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import { generateDemoData } from './constants/demoData';
import { parseMultiMeasureCSV, detectPhasesAndAugmentData } from './services/spc';
import type { DataPoint, ChartData } from './types';

const App: React.FC = () => {
    const [allData, setAllData] = useState<DataPoint[] | null>(null);
    const [chartData, setChartData] = useState<ChartData | null>(null);
    const [monitoredStations, setMonitoredStations] = useState<string[]>(['JFK', 'LAX', 'ORD']);
    const [selectedStation, setSelectedStation] = useState<string>('All Stations');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const processData = useCallback((data: DataPoint[]) => {
        setIsLoading(true);
        setError(null);
        try {
            const groupedByStationAndMeasure: { [station: string]: { [measure: string]: DataPoint[] } } = {};
            const stations = new Set<string>();

            for (const point of data) {
                stations.add(point.station);
                if (!groupedByStationAndMeasure[point.station]) {
                    groupedByStationAndMeasure[point.station] = {};
                }
                if (!groupedByStationAndMeasure[point.station][point.measure]) {
                    groupedByStationAndMeasure[point.station][point.measure] = [];
                }
                groupedByStationAndMeasure[point.station][point.measure].push(point);
            }

            const newChartData: ChartData = {};
            for (const station in groupedByStationAndMeasure) {
                newChartData[station] = {};
                for (const measure in groupedByStationAndMeasure[station]) {
                    const measureData = groupedByStationAndMeasure[station][measure];
                    measureData.sort((a, b) => a.date.getTime() - b.date.getTime());
                    newChartData[station][measure] = detectPhasesAndAugmentData(measureData);
                }
            }

            setChartData(newChartData);
            const foundStations = Array.from(stations);
            setMonitoredStations(prev => Array.from(new Set([...prev, ...foundStations])));

        } catch (e) {
            console.error(e);
            setError(e instanceof Error ? e.message : 'An unknown error occurred during data processing.');
            setChartData(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        if (allData) {
            processData(allData);
        }
    }, [allData, processData]);

    // Separate effect to handle station selection after data is processed
    useEffect(() => {
        if (chartData) {
            const availableStations = Object.keys(chartData);
            if (availableStations.length > 0) {
                // Only change selected station if current selection is invalid
                if (selectedStation !== 'All Stations' && !availableStations.includes(selectedStation)) {
                    setSelectedStation(availableStations[0]);
                }
            }
        }
    }, [chartData]);

    const handleLoadDemoData = useCallback(() => {
        const demoCsv = generateDemoData();
        try {
            const parsed = parseMultiMeasureCSV(demoCsv);
            setAllData(parsed);
        } catch (e) {
            console.error(e);
            setError(e instanceof Error ? e.message : 'Failed to parse demo data.');
        }
    }, []);

    const handleFileUpload = useCallback((file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target?.result as string;
            if (text) {
                try {
                    const parsed = parseMultiMeasureCSV(text);
                    setAllData(parsed);
                } catch (err) {
                    console.error(err);
                    setError(err instanceof Error ? err.message : 'Failed to parse uploaded CSV file.');
                }
            }
        };
        reader.onerror = () => {
             setError('Error reading file.');
        };
        reader.readAsText(file);
    }, []);

    const handleAddStation = (station: string) => {
        if (station && !monitoredStations.includes(station.toUpperCase())) {
            setMonitoredStations(prev => [...prev, station.toUpperCase()].sort());
        }
    };
    
    return (
        <div className="min-h-screen bg-gray-900 text-gray-200 flex flex-col">
            <Header
                onLoadDemoData={handleLoadDemoData}
                onFileUpload={handleFileUpload}
                monitoredStations={monitoredStations}
                onAddStation={handleAddStation}
                selectedStation={selectedStation}
                onSelectStation={setSelectedStation}
            />
            <main className="flex-grow p-4 sm:p-6 lg:p-8">
                <Dashboard
                    chartData={chartData}
                    selectedStation={selectedStation}
                    monitoredStations={monitoredStations}
                    isLoading={isLoading}
                    error={error}
                />
            </main>
        </div>
    );
};

export default App;