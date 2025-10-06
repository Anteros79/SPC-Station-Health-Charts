
export interface DataPoint {
  station: string;
  measure: string;
  date: Date;
  value: number;
}

export interface AugmentedDataPoint extends DataPoint {
  cl?: number;
  ucl?: number;
  lcl?: number;
}

export interface Phase {
  startIndex: number;
  endIndex: number;
  cl: number;
  ucl: number;
  lcl: number;
}

export interface AugmentedData {
  points: AugmentedDataPoint[];
  phases: Phase[];
}

export interface ChartData {
  [station: string]: {
    [measure: string]: AugmentedData;
  };
}
