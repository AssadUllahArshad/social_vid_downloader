export type PublishStatus = "IDEA" | "PLANNED" | "DRAFT" | "REVIEW" | "APPROVED" | "PUBLISHED" | "UPDATED" | "ARCHIVED" | "DEFERRED_FEATURE_NOT_READY";
export type Section = { heading: string; paragraphs: string[]; steps?: string[] };
export type Article = {
  path: string; canonical: string; platform: string; family: string;
  title: string; h1: string; description: string; primaryKeyword: string; secondaryKeywords: string[];
  intent: string; userBenefit: string; priority: number; targetDownloader: string | null; hub: string; contentRole?: "education";
  status: PublishStatus; indexable: boolean; intro: string; sections: Section[]; example: string;
  processingLinks?: string[];
  related: string[]; faq: { question: string; answer: string }[];
  sources: { title: string; url: string }[]; lastUpdated: string;
  review: { accuracy: boolean; distinctValue: boolean; answerFirst: boolean; supportedClaims: boolean; examples: boolean; specificity: boolean; reviewer: string; reviewedAt: string };
  inventoryApproval?: { approved: boolean; intent: string; path: string; rationale: string; reviewer: string; reviewedAt: string } | null;
  quality?: { passed: boolean; score: number; errors: string[] };
  approval?: { digest: string; reviewedAt: string; reviewer: string };
};
export type Disposition = {
  classification: "APPROVED_TO_WRITE" | "MERGE_WITH_EXISTING" | "REJECT_DUPLICATE" | "REJECT_CANNIBALIZATION" | "REJECT_LOW_VALUE" | "REJECT_UNSUPPORTED" | "NEEDS_RESEARCH" | "REJECTED_DUPLICATE" | "REJECTED_CANNIBALIZATION" | "REJECTED_LOW_VALUE" | "REJECTED_UNSUPPORTED" | "DEFERRED_FEATURE_NOT_READY";
  destination: string; reason: string; reviewedAt: string; targetUser: string;
  primaryQuestion: string; internalLinkDestination: string;
  outcome: "PUBLISHED" | "WRITE_REQUIRED" | "CONSOLIDATED" | "RESEARCH_REQUIRED" | "REJECTED" | "DEFERRED";
};
export type Brief = Pick<Article, "path" | "platform" | "family" | "title" | "h1" | "primaryKeyword" | "secondaryKeywords" | "intent" | "userBenefit" | "priority" | "targetDownloader" | "hub" | "status" | "indexable"> & { id?: string; batch?: string; disposition?: Disposition };
