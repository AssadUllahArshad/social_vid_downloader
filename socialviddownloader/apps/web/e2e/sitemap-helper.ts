import {expect,type APIRequestContext} from '@playwright/test';
export async function sitemapLocations(request:APIRequestContext){
 const response=await request.get('/sitemap.xml');expect(response.status()).toBe(200);
 const text=await response.text();const locations=(xml:string)=>[...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map(match=>match[1]);
 if(!text.includes('<sitemapindex'))return locations(text);
 const urls:string[]=[];
 for(const shard of locations(text)){const result=await request.get(new URL(shard).pathname);expect(result.status(),shard).toBe(200);urls.push(...locations(await result.text()));}
 return urls;
}
