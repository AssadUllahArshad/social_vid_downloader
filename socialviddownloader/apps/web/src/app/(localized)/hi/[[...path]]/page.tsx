import { LocalizedCore, localizedMetadata } from "@/components/localized-core";
import { corePaths } from "@/lib/localized-publication";
export const dynamicParams = false;
export function generateStaticParams() { return corePaths.map(path=>({path:path.split("/").filter(Boolean)})); }
export async function generateMetadata({params}:{params:Promise<{path?:string[]}>}) { const p=await params; return localizedMetadata("hi",p.path?.length?"/"+p.path.join("/")+"/":"/"); }
export default async function Page({params}:{params:Promise<{path?:string[]}>}) { const p=await params; return <LocalizedCore locale="hi" path={p.path?.length?"/"+p.path.join("/")+"/":"/"}/>; }
