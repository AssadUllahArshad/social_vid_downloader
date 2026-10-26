import {test, expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {statSync} from 'node:fs';
import errors from '../src/locales/snapchat-errors.json';

for (const [locale, messages] of Object.entries(errors)) test(`Snapchat error distinctions in ${locale}`, async ({page}) => {
  let code = 'snapchat_not_spotlight';
  await page.route(/\/api\/v1\/extract\/?$/, route => {
    expect(route.request().postDataJSON().url).toBe('https://snapchat.com/t/2mjmfV1D');
    return route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({success:false,error:{code,message:'Backend fallback'}})});
  });
  await page.goto(`${locale === 'en' ? '' : '/'+locale}/snapchat-spotlight-downloader/`);
  await page.locator('input[type=url]').fill('https://snapchat.com/t/2mjmfV1D');
  for (const [category, message] of Object.entries(messages)) {
    code = category;
    await page.locator('form button[type=submit]').click();
    await expect(page.locator('#download-message')).toHaveText(message);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
});

test('live public Spotlight share produces a verified video', async ({page}, info) => {
  test.skip(!process.env.SNAPCHAT_LIVE_URL, 'Explicit public source required; no live dependency in CI.');
  test.setTimeout(180000);
  await page.goto('/snapchat-spotlight-downloader/');
  await page.getByRole('textbox',{name:'Video URL'}).fill(process.env.SNAPCHAT_LIVE_URL!);
  await page.getByRole('button',{name:'Download',exact:true}).click();
  await expect(page.locator('.video-result')).toBeVisible({timeout:100000});
  await expect(page.getByRole('radio')).not.toHaveCount(0);
  await page.getByRole('button',{name:/^Prepare /}).click();
  const link = page.getByRole('link',{name:/Save file/});
  await expect(link).toBeVisible({timeout:60000});
  const pending = page.waitForEvent('download'); await link.click();
  const file = await (await pending).path();
  const probe = JSON.parse(execFileSync('ffprobe',['-v','error','-show_format','-show_streams','-of','json',file!],{encoding:'utf8'}));
  expect(probe.streams.some((s:{codec_type:string})=>s.codec_type==='video')).toBe(true);
  expect(Number(probe.format.duration)).toBeGreaterThan(0);
  execFileSync('ffmpeg',['-v','error','-i',file!,'-f','null','-'],{timeout:30000});
  await info.attach('verified-public-spotlight',{body:JSON.stringify({bytes:statSync(file!).size,duration:probe.format.duration,streams:probe.streams.map((s:{codec_type:string;codec_name:string;width:number;height:number})=>({type:s.codec_type,codec:s.codec_name,width:s.width,height:s.height}))}),contentType:'application/json'});
  await page.screenshot({path:info.outputPath('snapchat-share-ready.png'),fullPage:true});
});
