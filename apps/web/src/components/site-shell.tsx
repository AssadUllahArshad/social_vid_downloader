import Script from "next/script";
import { processingMessages } from "@/lib/processing-messages";
import Link from 'next/link';
import { Brand } from './brand';
import { LanguageSelector } from './language-selector';
import { LocaleProvider } from './locale-context';
import { dictionaries, type Locale } from '@/lib/i18n';
export function SiteShell({locale,children}:{locale:Locale;children:React.ReactNode}) {
 const text=dictionaries[locale];const prefix=locale==='en'?'':`/${locale}`;
 return <LocaleProvider locale={locale} messages={text}><Script src="https://analytics.ahrefs.com/analytics.js" data-key="VXk4fFdXMD+rwA2in6iQZA" strategy="afterInteractive" /><Script src="https://www.googletagmanager.com/gtag/js?id=G-HV6NYL5TEK" strategy="afterInteractive" />
 <Script id="google-analytics" strategy="afterInteractive">{`
   window.dataLayer = window.dataLayer || [];
   function gtag(){dataLayer.push(arguments);}
   gtag('js', new Date());
   gtag('config', 'G-HV6NYL5TEK');
 `}</Script><header className="header"><div className="container header-inner"><Brand href={`${prefix}/`} homeLabel={text.home}/><LanguageSelector/><nav aria-label={text.choose}><Link href={`${prefix}/#tools`}>{text.tools}</Link><Link href={`${prefix}/video-tools/`} hrefLang={locale}>{processingMessages[locale].hub}</Link><Link href={`${prefix}/guides/`}>{text.guides}</Link>{locale==='en'&&<Link href='/guides/general/'>Video help</Link>}<Link href={locale==='en'?'/#faq':`${prefix}/faq/`}>{text.faq}</Link></nav><Link className="header-action" href={`${prefix}/#download`}>{text.download}</Link></div></header>{children}<footer><div className="container"><div className="footer-top"><Brand href={`${prefix}/`} homeLabel={text.home}/><nav aria-label={text.help}>{[['about', '/about/'],['privacy','/privacy-policy/'],['terms','/terms/'],['copyright','/copyright/'],['contact','/contact/']].map(([key,path])=><Link key={path} href={path} hrefLang="en">{text[key as keyof typeof text]}</Link>)}</nav></div><p className="disclaimer">{text.notice}</p><p className="disclaimer">{text.independent}</p><div className="footer-bottom"><span>© {new Date().getFullYear()} SocialVidDownloader</span><a href="mailto:support@socialviddownloader.com"><bdi>support@socialviddownloader.com</bdi></a></div></div></footer></LocaleProvider>;
}
