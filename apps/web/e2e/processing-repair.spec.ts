import {test,expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
const directory=process.env.PROCESSING_REPAIR_MEDIA;
test.skip(!directory,'Requires prepared authorized realistic media.');
for(const name of ['silent.mp4','two-audio.mp4','source.mov','source.webm'])test(`real input variant ${name}`,async({page})=>{
 test.setTimeout(120000);await page.goto('/remove-audio-from-video/');await expect(page.locator('.processing-card fieldset')).toBeEnabled();
 await page.locator('input[type=file]').setInputFiles(join(directory!,name));
 await page.getByRole('button',{name:'Process files',exact:true}).click();
 const link=page.getByRole('link',{name:'Save file',exact:true});await expect(link).toBeVisible({timeout:90000});
 const pending=page.waitForEvent('download');await link.click();const path=await (await pending).path();
 const info=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',path!],{encoding:'utf8'}));
 expect(info.streams.map((s:{codec_type:string})=>s.codec_type)).toEqual(['video']);expect(Number(info.format.duration)).toBeGreaterThan(7);
 execFileSync('ffmpeg',['-v','error','-i',path!,'-f','null','-']);
});
test('cancel actual active processing and revoke delivery',async({page,request})=>{
 test.setTimeout(45000);await page.goto('/video-compressor/');await expect(page.locator('.processing-card fieldset')).toBeEnabled();
 await page.locator('input[type=file]').setInputFiles(process.env.PROCESSING_TRAILER_INPUT!);
 const created=page.waitForResponse(r=>r.url().endsWith('/api/processing/jobs/')&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Process files',exact:true}).click();const job=await (await created).json();
 await page.getByRole('button',{name:'Cancel',exact:true}).click();await expect(page.getByRole('link',{name:'Save file',exact:true})).toHaveCount(0);
 await expect.poll(async()=> (await (await request.get(job.statusUrl)).json()).status).toBe('cancelled');
 expect((await request.get(`/api/processing/files/${job.jobId}/`)).status()).toBe(410);
});
for(const locale of ['en','hi','ur','ar','bn','id','vi','th','pt-br','es','fr','de','tr'])test(`real invalid upload localized error ${locale}`,async({page})=>{
 const messages=JSON.parse(readFileSync(join(process.cwd(),'src/locales/processing',locale+'.json'),'utf8'));
 await page.goto(`${locale==='en'?'':'/'+locale}/video-converter/`);await expect(page.locator('.processing-card fieldset')).toBeEnabled();
 await page.locator('input[type=file]').setInputFiles({name:'invalid.mp4',mimeType:'video/mp4',buffer:Buffer.from('invalid media')});
 await page.getByRole('button',{name:messages.process,exact:true}).click();await expect(page.locator('.processing-card [role=alert]')).toHaveText(messages['error.invalid']);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
