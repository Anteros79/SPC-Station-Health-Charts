
const STATIONS = ['AUS', 'DAL', 'HOU'];  // Austin, Dallas Love Field, Houston Hobby
const MEASURES = ['Maintenance Cancels', 'Maintenance Delays', 'Scheduled Maintenance Findings', 'Unscheduled Maintenance'];

const generateRandomValue = (base: number, variance: number): number => {
    return base + (Math.random() - 0.5) * variance;
};

export const generateDemoData = (): string => {
    let csvContent = "station,measure,date,value\n";
    const dataPoints = [];
    const today = new Date();
    const numDays = 60;

    for (let i = numDays; i > 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateString = date.toISOString().split('T')[0];

        for (const station of STATIONS) {
            for (const measure of MEASURES) {
                let value = 0;
                
                // Introduce realistic process shifts
                if (station === 'DAL' && measure === 'Maintenance Delays') {
                    // Dallas shows improvement over time
                    if (i > numDays * 0.66) {
                        value = generateRandomValue(12, 3);  // Phase 1: Higher delays
                    } else if (i > numDays * 0.33) {
                        value = generateRandomValue(9, 2.5);  // Phase 2: Improved
                    } else {
                        value = generateRandomValue(7, 2);  // Phase 3: Best performance
                    }
                } else if (measure === 'Maintenance Cancels') {
                    value = generateRandomValue(2.0, 1.0);
                } else if (measure === 'Maintenance Delays') {
                    value = generateRandomValue(11, 3);
                } else if (measure === 'Scheduled Maintenance Findings') {
                    value = generateRandomValue(15, 4);
                } else if (measure === 'Unscheduled Maintenance') {
                    value = generateRandomValue(8, 3);
                }

                value = Math.max(0, parseFloat(value.toFixed(2))); // Ensure non-negative and format
                dataPoints.push(`${station},"${measure}",${dateString},${value}`);
            }
        }
    }
    
    csvContent += dataPoints.join('\n');
    return csvContent;
};
