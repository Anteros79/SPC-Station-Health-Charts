
import React, { useState, useRef } from 'react';

interface HeaderProps {
    onLoadDemoData: () => void;
    onFileUpload: (file: File) => void;
    monitoredStations: string[];
    onAddStation: (station: string) => void;
    selectedStation: string;
    onSelectStation: (station: string) => void;
}

const Header: React.FC<HeaderProps> = ({
    onLoadDemoData,
    onFileUpload,
    monitoredStations,
    onAddStation,
    selectedStation,
    onSelectStation
}) => {
    const [newStation, setNewStation] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            onFileUpload(file);
        }
    };

    const handleAddClick = () => {
        onAddStation(newStation);
        setNewStation('');
    };

    const triggerFileSelect = () => {
        fileInputRef.current?.click();
    };

    return (
        <header className="bg-gray-800 shadow-md p-4 border-b border-gray-700">
            <div className="container mx-auto flex flex-wrap items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-cyan-400 whitespace-nowrap">
                    Airline Tech Ops SPC Dashboard
                </h1>

                <div className="flex flex-wrap items-center gap-4 w-full lg:w-auto">
                    {/* Data Loading Controls */}
                    <div className="flex items-center gap-2">
                        <button
                            onClick={onLoadDemoData}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        >
                            Load Demo
                        </button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            className="hidden"
                            accept=".csv"
                        />
                        <button
                            onClick={triggerFileSelect}
                            className="bg-gray-700 hover:bg-gray-600 text-gray-200 font-semibold py-2 px-4 rounded-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                        >
                            Upload CSV
                        </button>
                    </div>

                    {/* Station Controls */}
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            value={newStation}
                            onChange={(e) => setNewStation(e.target.value.toUpperCase())}
                            placeholder="Add Station (e.g., SFO)"
                            className="bg-gray-700 border border-gray-600 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-40"
                        />
                        <button
                            onClick={handleAddClick}
                            className="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                        >
                            Add
                        </button>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <label htmlFor="station-select" className="font-semibold">View:</label>
                        <select
                            id="station-select"
                            value={selectedStation}
                            onChange={(e) => onSelectStation(e.target.value)}
                            className="bg-gray-700 border border-gray-600 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                        >
                            <option value="All Stations">All Stations</option>
                            {monitoredStations.map(station => (
                                <option key={station} value={station}>{station}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
