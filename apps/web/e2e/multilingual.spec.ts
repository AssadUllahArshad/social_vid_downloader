import {sitemapLocations} from './sitemap-helper';
import {test,expect} from '@playwright/test';
const names={hi:'हिन्दी',ur:'اردو',ar:'العربية',bn:'বাংলা',id:'Bahasa Indonesia',vi:'Tiếng Việt',th:'ไทย','pt-br':'Português (Brasil)',es:'Español',fr:'Français',de:'Deutsch',tr:'Türkçe'};
test('locale switching preserves equivalents and falls back for untranslated articles',async({page})=>{
 await page.goto('/facebook-video-downloader/');
 if(!(await page.locator('.language-selector').getAttribute('open') !== null)) await page.locator('.language-selector summary').click(); await page.locator('.language-menu a[lang=hi]').click();
 await expect(page).toHaveURL(/\/hi\/facebook-video-downloader\/$/);
 await expect(page.locator('html')).toHaveAttribute('lang','hi');
 if(!(await page.locator('.language-selector').getAttribute('open') !== null)) await page.locator('.language-selector summary').click(); await page.locator('.language-menu a[lang=en]').click();
 await expect(page).toHaveURL(/\/facebook-video-downloader\/$/);
 await page.goto('/guides/general/video-container-vs-codec/');
 if(!(await page.locator('.language-selector').getAttribute('open') !== null)) await page.locator('.language-selector summary').click(); await page.locator('.language-menu a[lang=ar]').click();
 await expect(page).toHaveURL(/\/ar\/$/);
});
test('core locales are server-rendered with canonical language and complete controls',async({page,request})=>{
 for(const [locale,name] of Object.entries(names)){
  const response=await request.get(`/${locale}/youtube-video-downloader/`);expect(response.status()).toBe(200);
  const html=await response.text();expect(html).toContain(`lang="${locale==='pt-br'?'pt-BR':locale}"`);expect(html).toContain(`href="https://socialviddownloader.com/${locale}/youtube-video-downloader/"`);
  await page.goto(`/${locale}/`);await expect(page.locator('.language-selector summary')).toContainText(name);
  expect((await request.get(`/${locale}/snapchat-story-downloader/`)).status()).toBe(404);
 }
});
test('Arabic and Urdu support mobile widths and keyboard language selection',async({page})=>{
 for(const locale of ['ar','ur'])for(const width of [320,360,375,390,414,768,1280,1366,1440,1920]){
  await page.setViewportSize({width,height:900});await page.goto(`/${locale}/instagram-reels-downloader/`);
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  expect(await page.locator('input[type=url]').evaluate(el=>getComputedStyle(el).direction)).toBe('ltr');
  const selector=page.locator('.language-selector summary');await selector.focus();await expect(selector).toBeFocused(); await selector.press('Enter'); await expect(page.locator('.language-menu a')).toHaveCount(13); await expect(page.locator('.language-menu a[lang=tr]')).toBeVisible(); const bounds=await page.locator('.language-menu').boundingBox(); expect(bounds!.x).toBeGreaterThanOrEqual(0); expect(bounds!.x+bounds!.width).toBeLessThanOrEqual(width+1); await selector.press('Escape'); await expect(page.locator('.language-selector')).not.toHaveAttribute('open','');
 }
});
test('localized downloader calls the existing API and hides raw English errors',async({page})=>{
 await page.route('**/api/v1/capabilities/',route=>route.fulfill({json:{providers:[]}}));
 let called=false;await page.route('**/api/v1/extract/',route=>{called=true;expect(route.request().postDataJSON().platform).toBe('youtube');return route.fulfill({status:422,json:{success:false,error:{code:'authentication_required',message:'Private internal English diagnostic'}}});});
 await page.goto('/ar/youtube-video-downloader/');await page.locator('input[type=url]').fill('https://www.youtube.com/watch?v=jNQXAC9IVRw');await page.locator('button[type=submit]').click();await expect(page.locator('[role=alert]').first()).toBeVisible();expect(called).toBe(true);await expect(page.locator('main')).not.toContainText('Private internal English diagnostic');
});

test('reciprocal alternates and localized sitemap exclude unsupported equivalents',async({request})=>{
 const english=await (await request.get('/facebook-video-downloader/')).text();
 const hindi=await (await request.get('/hi/facebook-video-downloader/')).text();
 for(const html of [english,hindi])for(const code of ['en','hi','ur','ar','bn','id','vi','th','pt-BR','es','fr','de','tr','x-default'])expect(html).toMatch(new RegExp(`hreflang="${code}"`,"i"));
 const sitemap=(await sitemapLocations(request)).join('\n');
 expect(sitemap).toContain('https://socialviddownloader.com/hi/facebook-video-downloader/');
 expect(sitemap).not.toContain('/hi/faq/');expect(sitemap).not.toContain('story-downloader');
 const faq=await(await request.get('/hi/faq/')).text();expect(faq).toContain('noindex, follow');
});

test('localized processing forms remain usable in RTL and their metadata is reciprocal',async({page,request})=>{for(const locale of ['ar','ur']){await page.goto(`/${locale}/trim-video/`);await expect(page.locator('html')).toHaveAttribute('dir','rtl');await expect(page.locator('.processing-card fieldset')).toBeEnabled();await expect(page.locator('input[type=file]')).toHaveCount(1);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);const html=await(await request.get(`/${locale}/trim-video/`)).text();expect(html).toContain(`href="https://socialviddownloader.com/${locale}/trim-video/"`);expect(html).toMatch(/hreflang="x-default"/i);}});

 test("Portuguese and German tablet navigation stays within viewport",async({page})=>{await page.setViewportSize({width:768,height:900});for(const locale of ["pt-br","de"]){await page.goto(`/${locale}/youtube-video-downloader/`);expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(768);}});
