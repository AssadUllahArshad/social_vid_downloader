import {test, expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {statSync, readFileSync} from 'node:fs';
import {join} from 'node:path';

const trailer = process.env.PROCESSING_TRAILER_INPUT;
if(!trailer) test.skip(true,'Requires PROCESSING_TRAILER_INPUT');

const tools = JSON.parse(readFileSync(join(__dirname,'../../../content/processing/tools.json'),'utf8')) as Array<{slug:string,id:string}>;

for(const tool of tools){
  test(`realistic processing ${tool.slug}` , async({page},info)=>{
    test.setTimeout(300000);
    const path = `/${tool.slug}/`;
    await page.goto(path);
    await expect(page.locator('.processing-card fieldset')).toBeEnabled();
    await page.locator('input[type=file]').setInputFiles(trailer!);
    await page.getByRole('button',{name:'Process files',exact:true}).click();
    const link=page.getByRole('link',{name:'Save file',exact:true});
    // Some tools may not provide a downloadable output; wait and then check
    await expect(link).toBeVisible({timeout:240000});
    const pending=page.waitForEvent('download'); await link.click(); const download=await pending; const file=await download.path();
    expect(statSync(file!).size).toBeGreaterThan(0);
    // run ffprobe to verify media streams
    const probeRaw=execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file!],{encoding:'utf8'});
    const probe=JSON.parse(probeRaw) as {format?:{duration?:string};streams?:Array<{codec_type?:string;codec_name?:string}>};
    execFileSync('ffmpeg',['-v','error','-i',file!,'-f','null','-'],{timeout:120000});
    await info.attach('verified-output',{body:JSON.stringify({tool:tool.slug,inputBytes:statSync(trailer!).size,outputBytes:statSync(file!).size,duration:probe.format?.duration,streams:probe.streams?.map((s)=>({type:s.codec_type,codec:s.codec_name}))}),contentType:'application/json'});
  });
}
