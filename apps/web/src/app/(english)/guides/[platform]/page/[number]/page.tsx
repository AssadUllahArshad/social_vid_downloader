import { GuideCollection, collectionPaths, collectionMetadata } from "@/components/guide-collection";
type Props = { params: Promise<{ platform: string; number: string }> };
export function generateStaticParams() { return collectionPaths("platform").filter(row => row.number !== "1").map(row => ({ platform: row.key, number: row.number })); }
export async function generateMetadata({ params }: Props) {
  const { platform, number } = await params;
  return collectionMetadata("platform", platform, number, true);
}
export default async function Directory({ params }: Props) {
  const { platform, number } = await params;
  collectionMetadata("platform", platform, number, true);
  return <GuideCollection kind="platform" group={platform} number={Number(number)} />;
}
