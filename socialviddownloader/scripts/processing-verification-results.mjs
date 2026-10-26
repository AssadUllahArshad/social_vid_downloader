export function toolResults(tools, report) {
  const specs = [];
  const collect = suite => { specs.push(...(suite.specs || [])); for (const child of suite.suites || []) collect(child); };
  collect(report);
  return tools.map(tool => {
    const tests = specs.filter(row => row.title === `real browser upload and verified output: ${tool.id}`).flatMap(row => row.tests);
    const projects = Object.fromEntries(['desktop', 'mobile'].map(project => {
      const test = tests.find(row => row.projectName === project);
      return [project, test?.results.at(-1)?.status === 'passed' ? 'PASS' : 'FAIL'];
    }));
    return {operation: tool.id, name: tool.name, route: `/${tool.slug}/`, ...projects,
      status: Object.values(projects).every(value => value === 'PASS') ? 'VERIFIED' : 'ERROR'};
  });
}
