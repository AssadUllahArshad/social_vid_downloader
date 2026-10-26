import {test,expect} from '@playwright/test';
const paths=['/','/youtube-video-downloader/','/video-converter/','/guides/general/video-container-vs-codec/','/ar/','/ar/youtube-video-downloader/','/ar/video-converter/','/ur/','/ur/youtube-video-downloader/','/ur/video-converter/'];
test('global styles and matching assets load across page roots and viewports',async({page,request})=>{
 test.setTimeout(180000);
 const assetErrors:string[]=[];
 page.on('console',message=>{if(message.type()==='error'&&/stylesheet|MIME type|chunk|CSS/i.test(message.text()))assetErrors.push(message.text());});
 page.on('response',response=>{if(response.url().includes('/_next/static/')&&response.status()>=400)assetErrors.push(`${response.status()} ${response.url()}`);});
 for(const path of paths)for(const width of [320,390,768,1366,1920]){
  await page.setViewportSize({width,height:900});const response=await page.goto(path,{waitUntil:'networkidle'});expect(response?.status(),path).toBe(200);
  await expect(page.locator('body')).toHaveCSS('font-family','Arial, Helvetica, sans-serif');
  await expect(page.locator('.header-inner > nav')).toHaveCSS('display','flex');
  await expect(page.locator('.header .brand')).toHaveCSS('text-decoration-line','none');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth),`${path} ${width}`).toBeLessThanOrEqual(width+1);
  const rtl=path.startsWith('/ar/')||path.startsWith('/ur/');await expect(page.locator('html')).toHaveAttribute('dir',rtl?'rtl':'ltr');
  const css=await page.locator('link[rel=stylesheet]').evaluateAll(elements=>elements.map(element=>(element as HTMLLinkElement).href));expect(css.length).toBeGreaterThan(0);
  for(const url of css){const asset=await request.get(url);expect(asset.status(),url).toBe(200);expect(asset.headers()['content-type']).toMatch(/^text\/css/);const text=await asset.text();expect(text).toContain('--accent');expect(text).toContain('@layer');}
 }
 expect(assetErrors).toEqual([]);
});
