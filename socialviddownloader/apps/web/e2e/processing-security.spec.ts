import {test,expect} from '@playwright/test';
test('processing proxy rejects foreign origins and unknown routes',async({request})=>{
 const foreign=await request.post('/api/processing/jobs',{headers:{origin:'https://attacker.example'},data:{}});expect(foreign.status()).toBe(403);
 const unknown=await request.get('/api/processing/private-config');expect(unknown.status()).toBe(404);
 const oversize=await request.post('/api/processing/jobs',{data:'x'.repeat(8193)});expect(oversize.status()).toBe(413);
 expect(oversize.headers()['cache-control']).toBe('no-store');
});
