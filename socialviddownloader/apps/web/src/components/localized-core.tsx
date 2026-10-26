import { ProcessingPage } from "./processing-page";
import { processingPaths, processingTools } from "@/lib/processing-tools";
import { processingMessages } from "@/lib/processing-messages";
import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { dictionaries, type Locale } from '@/lib/i18n';
import { tools, site } from '@/lib/content';
import { Downloader } from './downloader';
import { JsonLd } from './json-ld';
import { corePaths, translatedIndexable, equivalentLanguages } from '@/lib/localized-publication';
export function localizedTitle(locale:Locale,path:string) {
 if(processingPaths.includes(path)) { const tool=processingTools.find(tool=>`/${tool.slug}/`===path); return tool?processingMessages[locale]["title."+tool.id]:processingMessages[locale].hub; }
 const text=dictionaries[locale];const slug=path.split('/')[1];const tool=tools.find(t=>t.slug===slug&&['integrated','beta'].includes(t.status));
 if(path==='/')return text.title;
 if(path==='/guides/')return text.guides;
 if(path==='/faq/')return text.faq;
 if(tool)return `${tool.platform} ${text[(tool.kind.toLowerCase() as 'video'|'reels'|'shorts'|'spotlight')]} — ${text.download}`;
 return `${slug==='snapchat-downloader'?'Snapchat':({facebook:"Facebook",instagram:"Instagram",youtube:"YouTube",tiktok:"TikTok"} as Record<string,string>)[slug] || slug} — ${text.tools}`;
}
export function localizedMetadata(locale:Locale,path:string):Metadata {
 const title=localizedTitle(locale,path);const text=dictionaries[locale];const index=translatedIndexable(locale,path);const description=processingPaths.includes(path)?processingMessages[locale].intro:text.intro;
 return { title,description:`${title}. ${description}`,alternates:{canonical:`/${locale}${path}`,languages:index?equivalentLanguages(path):undefined},robots:{index,follow:true},openGraph:{title,description,url:`${site}/${locale}${path}`,locale:locale==='pt-br'?'pt_BR':locale},twitter:{card:'summary',title,description}};
}
export function LocalizedCore({locale,path}:{locale:Locale;path:string}) {
 if(!corePaths.includes(path))notFound(); if(processingPaths.includes(path))return <ProcessingPage locale={locale} slug={path.split("/")[1]}/>;const text=dictionaries[locale];const prefix=`/${locale}`;const slug=path.split('/')[1];const tool=tools.find(t=>t.slug===slug&&['integrated','beta'].includes(t.status));const title=localizedTitle(locale,path);
 const platform=tool?.platform||(slug==='snapchat-downloader'?'Snapchat':['facebook','instagram','youtube','tiktok'].includes(slug)?slug:null);
 const activeTools=tools.filter(t=>['integrated','beta'].includes(t.status)&&(!platform||t.platform.toLowerCase()===platform.toLowerCase()));
 return <main className="container content-page"><nav className="breadcrumb" aria-label={text.home}><Link href={`${prefix}/`}>{text.home}</Link>{path!=='/'&&<> / <span>{title}</span></>}</nav><h1>{title}</h1><p>{path==='/guides/'?text.guidesIntro:text.intro}</p>
 {(path==='/'||tool)&&<section id="download"><Downloader platform={tool?.platform} contentType={tool?.kind.toLowerCase()} capabilityState={tool?.capabilityState as 'AVAILABLE'|'BETA'|undefined}/></section>}
 {tool&&<p className="notice"><bdi>{tool.platform}</bdi> · {tool.capabilityState==='BETA'?text.beta:text.available}</p>}
 {(path==='/'||platform||path==='/guides/')&&<section id="tools"><h2>{text.tools}</h2>{path==='/'&&<div className='related'>{['facebook','instagram','youtube','tiktok','snapchat-downloader'].map(hub=><Link key={hub} href={`${prefix}/${hub}/`}>{localizedTitle(locale,`/${hub}/`)}</Link>)}</div>}<div className="related">{activeTools.map(t=><Link href={`${prefix}/${t.slug}/`} key={t.slug}>{localizedTitle(locale,`/${t.slug}/`)}</Link>)}</div></section>}
 {path==='/guides/'&&<p><Link href='/guides/' hrefLang='en' lang='en'>English: {dictionaries.en.guides}</Link></p>}
 <section><h2>{text.help}</h2><p>{text.instructions}</p><h2>{text.quality}</h2><p>{text.chooseFormat}</p><h2>{text.audio}</h2><p>{text.audioHelp}</p><p className="notice">{text.limitations}</p></section>
 <section id="faq"><h2>{text.faq}</h2><details><summary>{text.faqQuestion}</summary><p>{text.faqAnswer}</p></details><p>{text.notice}</p></section>
 <p><Link href={`${prefix}/guides/`}>{text.guides}</Link> · <Link href={`${prefix}/faq/`}>{text.faq}</Link></p>
 <JsonLd data={{'@context':'https://schema.org','@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:text.home,item:`${site}${prefix}/`},...(path==='/'?[]:[{'@type':'ListItem',position:2,name:title,item:`${site}${prefix}${path}`}])]}}/>
 </main>;
}
