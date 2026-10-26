import { processingMessages } from "@/lib/processing-messages";
import Link from 'next/link';
import { Brand } from './brand';
import { LanguageSelector } from './language-selector';
import { LocaleProvider } from './locale-context';
import { dictionaries, type Locale } from '@/lib/i18n';
export function SiteShell({locale,children}:{locale:Locale;children:React.ReactNode}) {
 const text=dictionaries[locale];const prefix=locale==='en'?'':`/${locale}`;
 return <LocaleProvider locale={locale} messages={text}><header className="header"><div className="container header-inner"><Brand href={`${prefix}/`} homeLabel={text.home}/><LanguageSelector/><nav aria-label={text.choose}><Link href={`${prefix}/#tools`}>{text.tools}</Link><Link href={`${prefix}/video-tools/`} hrefLang={locale}>{processingMessages[locale].hub}</Link><Link href={`${prefix}/guides/`}>{text.guides}</Link>{locale==='en'&&<Link href='/blog/'>{text.resources}</Link>}<Link href={locale==='en'?'/#faq':`${prefix}/faq/`}>{text.faq}</Link></nav><Link className="header-action" href={`${prefix}/#download`}>{text.download}</Link></div></header>{children}<footer><div className="container"><div className="footer-top"><Brand href={`${prefix}/`} homeLabel={text.home}/><nav aria-label={text.help}>{[['about', '/about/'],['privacy','/privacy-policy/'],['terms','/terms/'],['copyright','/copyright/'],['contact','/contact/']].map(([key,path])=><Link key={path} href={path} hrefLang="en">{text[key as keyof typeof text]}</Link>)}</nav></div><p className="disclaimer">{text.notice}</p><p className="disclaimer">{text.independent}</p><div className="footer-bottom"><span>© {new Date().getFullYear()} SocialVidDownloader</span><a href="mailto:support@socialviddownloader.com"><bdi>support@socialviddownloader.com</bdi></a></div></div></footer></LocaleProvider>;
}
