import tools from "../../../content/processing/tools.json";
import {test,expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,writeFileSync,readFileSync,statSync,copyFileSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
test.skip(process.env.PROCESSING_REAL_E2E!=='1','Explicit loopback processing server required; normal CI uses controlled tests.');
const operations=tools.map(tool=>[tool.id,tool.slug]);
let folder:string,input:string;
let image:string,gif:string,subtitle:string,embedded:string;
test.beforeAll(()=>{folder=mkdtempSync(join(tmpdir(),'svd-processing-browser-'));input=join(folder,'input.mp4');if(process.env.PROCESSING_REAL_INPUT)copyFileSync(process.env.PROCESSING_REAL_INPUT,input);else execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','testsrc=size=160x90:rate=10','-f','lavfi','-i','sine=frequency=440','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',input]); image=join(folder,'image.png');gif=join(folder,'input.gif');subtitle=join(folder,'subtitles.srt');embedded=join(folder,'embedded.mkv');execFileSync('ffmpeg',['-v','error','-y','-i',input,'-frames:v','1',image]);execFileSync('ffmpeg',['-v','error','-y','-i',input,'-an','-vf','fps=5',gif]);writeFileSync(subtitle,'1\n00:00:00,000 --> 00:00:01,500\nAuthorized test caption\n');execFileSync('ffmpeg',['-v','error','-y','-i',input,'-i',subtitle,'-map','0:v:0','-map','0:a:0','-map','1:s:0','-c','copy',embedded]);});
test.afterAll(()=>{if(folder)rmSync(folder,{recursive:true,force:true});});
for(const [operation,slug] of operations)test(`real browser upload and verified output: ${operation}`,async({page},testInfo)=>{
 test.setTimeout(240000);
 await page.goto(`/${slug}/`);await expect(page.locator('.processing-card fieldset')).toBeEnabled();
 await page.locator('input[type=file]').setInputFiles(operation==='merger'?[input,input]:operation==='images'?[image,image]:operation==='image-watermark'?[input,image]:operation==='burn-subtitles'?[input,subtitle]:operation==='gif-to-video'?gif:operation==='extract-subtitles'?embedded:input);
 if(operation==='trimmer'){await page.locator('input[name=start]').fill('0.2');await page.locator('input[name=end]').fill('1.2');}
 if(operation==='text-watermark')await page.locator('input[name=text]').fill('Authorized sample'); if(operation==='splitter')await page.locator('input[name=segment_seconds]').fill('1');
 if(operation==='video-to-gif')await page.locator('input[name=end]').fill('1.5');
 await page.getByRole('button',{name:'Process files',exact:true}).click();
 await expect(page.locator('.processing-card a.download-button, .processing-card [role=alert]')).toBeVisible({timeout:210000});await expect(page.locator('.processing-card [role=alert]')).toHaveCount(0);const link=page.getByRole('link',{name:'Save file',exact:true});await expect(link).toBeVisible();
 const waiting=page.waitForEvent('download');await link.click();const download=await waiting;const path=await download.path();expect(path).toBeTruthy();await expect(page.locator('.processing-card section')).toContainText(`${statSync(path!).size} B`);
 if(operation==='remove-audio')await page.screenshot({path:testInfo.outputPath('verified-mute.png'),fullPage:true});
 if(operation==='information'){expect(JSON.parse(readFileSync(path!,'utf8')).duration).toBeGreaterThan(0);return;}if(operation==='extract-subtitles'){expect(readFileSync(path!,'utf8')).toContain('Authorized test caption');return;}if(operation==='splitter'){expect(readFileSync(path!).subarray(0,2).toString()).toBe('PK');const extracted=join(folder,'segments-'+testInfo.project.name);execFileSync('unzip',['-o',path!,'-d',extracted]);for(const file of readdirSync(extracted)){const part=JSON.parse(execFileSync('ffprobe',['-v','error','-show_format','-of','json',join(extracted,file)],{encoding:'utf8'}));expect(Number(part.format.duration)).toBeGreaterThan(0);}return;}
 const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',path!],{encoding:'utf8'}));
 execFileSync('ffmpeg',['-v','error','-i',path!,'-f','null','-'],{timeout:120000});
 expect(Number(probe.format.size)).toBeGreaterThan(0);const streams=probe.streams.map((s:{codec_type:string})=>s.codec_type);
 expect(streams).toContain(operation==='mp3'?'audio':'video');if(operation==='remove-audio')expect(streams).not.toContain('audio');
 if(operation==='trimmer')expect(Number(probe.format.duration)).toBeCloseTo(1,0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
