"use client";
import { useEffect, useRef } from "react";
import { useLocale } from "./locale-context";
import { usePathname } from "next/navigation";
import { languageNames, locales, splitLocale, localeDestination } from "@/lib/locale-routing";
export function LanguageSelector() {
  const context = useLocale();
  const path = usePathname();
  const { locale, englishPath } = splitLocale(path);
  const menu = useRef<HTMLDetailsElement>(null);
  const previousPath = useRef(path);
  useEffect(() => { if (previousPath.current !== path && menu.current) menu.current.open = false; previousPath.current = path; }, [path]);
  const label = context?.messages.choose || "Choose language";
  return <details ref={menu} className="language-selector" onKeyDown={event => { if(event.key === "Escape" && menu.current) { menu.current.open = false; menu.current.querySelector("summary")?.focus(); } }}><summary aria-label={label}><span aria-hidden="true">🌐</span> {languageNames[locale]}</summary>
    <nav aria-label={label} className="language-menu">{locales.map(code=><a key={code} href={localeDestination(code,englishPath)} lang={code==='pt-br'?'pt-BR':code} hrefLang={code==='pt-br'?'pt-BR':code} aria-current={code===locale?"true":undefined} onClick={()=>{try{localStorage.setItem("svd-language",code);}catch{/* Optional storage. */}}}>{languageNames[code]}</a>)}</nav>
  </details>;
}
