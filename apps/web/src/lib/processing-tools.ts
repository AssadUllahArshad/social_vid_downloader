import records from '../../../../content/processing/tools.json';
export const processingTools=records;
export const processingPaths=['/video-tools/',...records.map(tool=>`/${tool.slug}/`)];
