import { GuideCollection, collectionPaths, collectionMetadata } from "@/components/guide-collection";
type Props = { params: Promise<{ platform: string }> };
export function generateStaticParams() { return collectionPaths("platform").filter(row => row.number === "1").map(row => ({ platform: row.key })); }
export async function generateMetadata({ params }: Props) {
  const { platform } = await params;
  return collectionMetadata("platform", platform);
}
export default async function Directory({ params }: Props) {
  const { platform } = await params;
  return <GuideCollection kind="platform" group={platform} />;
}
