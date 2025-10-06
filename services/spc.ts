import type { DataPoint, AugmentedData, AugmentedDataPoint, Phase } from '../types';

export const parseMultiMeasureCSV = (csvText: string): DataPoint[] => {
    const lines = csvText.trim().split('\n');
    const header = lines.shift()?.trim().split(',').map(h => h.trim()) || [];
    
    const colIndices = {
        station: header.indexOf('station'),
        measure: header.indexOf('measure'),
        date: header.indexOf('date'),
        value: header.indexOf('value'),
    };

    if (Object.values(colIndices).some(index => index === -1)) {
        throw new Error('CSV must contain headers: station, measure, date, value');
    }

    return lines.map((line, index) => {
        const values = line.trim().split(',');
        if (values.length !== header.length) {
            console.warn(`Skipping malformed CSV line ${index + 2}: ${line}`);
            return null;
        }

        const value = parseFloat(values[colIndices.value]);
        if (isNaN(value)) {
            console.warn(`Skipping line ${index + 2} due to invalid numeric value.`);
            return null;
        }

        const date = new Date(values[colIndices.date]);
        if (isNaN(date.getTime())) {
            console.warn(`Skipping line ${index + 2} due to invalid date format.`);
            return null;
        }

        return {
            station: values[colIndices.station].trim(),
            measure: values[colIndices.measure].trim(),
            date: date,
            value: value,
        };
    }).filter((p): p is DataPoint => p !== null);
};


export const detectPhasesAndAugmentData = (data: DataPoint[]): AugmentedData => {
    if (data.length < 2) {
        return { points: data, phases: [] };
    }

    const phases: Phase[] = [];
    const augmentedPoints: AugmentedDataPoint[] = data.map(p => ({...p}));

    let currentPhaseStartIndex = 0;

    while (currentPhaseStartIndex < data.length) {
        const remainingData = data.slice(currentPhaseStartIndex);
        if (remainingData.length === 0) break;
        
        // Calculate initial limits for the potential phase
        let tempPhaseData = remainingData;
        let { cl, mR_bar } = calculateInitialLimits(tempPhaseData);
        let ucl = cl + 2.66 * mR_bar;
        let lcl = Math.max(0, cl - 2.66 * mR_bar);

        // Find the end of the current stable phase
        let phaseEndIndexInData = findPhaseEnd(remainingData, cl) + currentPhaseStartIndex;
        
        // This handles an edge case where a shift is detected at the very start of a segment.
        // It prevents an empty slice and a potential infinite loop by ensuring the phase is at least one point long.
        if (phaseEndIndexInData < currentPhaseStartIndex) {
            phaseEndIndexInData = currentPhaseStartIndex;
        }

        // Recalculate limits based on the actual detected phase
        const finalPhaseData = data.slice(currentPhaseStartIndex, phaseEndIndexInData + 1);
        const finalLimits = calculateInitialLimits(finalPhaseData);
        cl = finalLimits.cl;
        mR_bar = finalLimits.mR_bar;
        ucl = cl + 2.66 * mR_bar;
        lcl = Math.max(0, cl - 2.66 * mR_bar);

        phases.push({
            startIndex: currentPhaseStartIndex,
            endIndex: phaseEndIndexInData,
            cl, ucl, lcl
        });

        // Augment points with calculated limits for this phase
        for (let i = currentPhaseStartIndex; i <= phaseEndIndexInData; i++) {
            if (augmentedPoints[i]) {
                augmentedPoints[i].cl = cl;
                augmentedPoints[i].ucl = ucl;
                augmentedPoints[i].lcl = lcl;
            }
        }

        currentPhaseStartIndex = phaseEndIndexInData + 1;
    }

    return { points: augmentedPoints, phases };
};

const calculateInitialLimits = (data: DataPoint[]) => {
    if (data.length === 0) return { cl: 0, mR_bar: 0 };
    if (data.length === 1) return { cl: data[0].value, mR_bar: 0 };

    const sum = data.reduce((acc, p) => acc + p.value, 0);
    const cl = sum / data.length;

    const movingRanges: number[] = [];
    for (let i = 1; i < data.length; i++) {
        movingRanges.push(Math.abs(data[i].value - data[i-1].value));
    }

    const mR_sum = movingRanges.reduce((acc, mr) => acc + mr, 0);
    const mR_bar = movingRanges.length > 0 ? mR_sum / movingRanges.length : 0;

    return { cl, mR_bar };
};

const findPhaseEnd = (data: DataPoint[], cl: number): number => {
    // SPC rule: 8 consecutive points on one side of the center line
    const RUN_LENGTH = 8;

    if (data.length < RUN_LENGTH) {
        return data.length - 1; // Not enough data for a run, phase is the whole set
    }
    
    let consecutiveAbove = 0;
    let consecutiveBelow = 0;

    for (let i = 0; i < data.length; i++) {
        if (data[i].value > cl) {
            consecutiveAbove++;
            consecutiveBelow = 0;
        } else if (data[i].value < cl) {
            consecutiveBelow++;
            consecutiveAbove = 0;
        } else {
            consecutiveAbove = 0;
            consecutiveBelow = 0;
        }

        if (consecutiveAbove >= RUN_LENGTH || consecutiveBelow >= RUN_LENGTH) {
            // The shift starts at the beginning of this run.
            // So the previous phase ends at the point just before the run started.
            return i - RUN_LENGTH;
        }
    }

    return data.length - 1; // No shift detected, phase is the whole set
};