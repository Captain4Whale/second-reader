import type { ReactionId, ReactionType } from "../lib/contract";

export const LANDING_REACTION_CARDS = [
  {
    key: "highlight",
    accentType: "highlight",
    title: "Highlight",
    description: "Surface the sentence the agent thinks is most worth carrying forward.",
  },
  {
    key: "association",
    accentType: "association",
    title: "Association",
    description: "Connect a passage to nearby ideas, frameworks, or outside patterns.",
  },
  {
    key: "discern",
    accentType: "discern",
    title: "Discern",
    description: "Sharpen the distinction, tension, or hidden tradeoff inside a claim.",
  },
  {
    key: "retrospect",
    accentType: "retrospect",
    title: "Retrospect",
    description: "Call back to earlier threads in the book when the current passage reactivates them.",
  },
  {
    key: "curious",
    accentType: "curious",
    title: "Curious",
    description: "Push into missing evidence, edge cases, and questions worth searching.",
  },
  {
    key: "marks",
    accentType: "highlight",
    title: "Known / Blindspot",
    description: "Use marks to separate what already felt familiar from what actually changed your map.",
  },
] as const satisfies ReadonlyArray<{
  key: string;
  accentType: ReactionType;
  title: string;
  description: string;
}>;

export const LANDING_CONTRACT_NOTES = [
  "The canonical web routes are `/`, `/books`, `/books/:id`, `/books/:id/analysis`, `/books/:id/chapters/:chapterId`, and `/marks`.",
  "All public IDs are integers at the API boundary, even though the backend still stores legacy slug/hash identifiers internally.",
  "The upload flow remains available at `/upload` as a utility route, but it is not part of the canonical navigation contract.",
] as const;

export const LANDING_SAMPLE_TEASERS = [
  {
    reactionId: 4101,
    type: "highlight",
    chapterRef: "Chapter 1",
    sectionRef: "1.1",
    anchorQuote: "You do not enter relationships with value, you enter relationships as value.",
    content: "The sentence reframes attraction as exchange structure, not mood or moral approval.",
  },
  {
    reactionId: 4102,
    type: "discern",
    chapterRef: "Chapter 1",
    sectionRef: "1.2",
    anchorQuote: "Rules and laws govern behavior because they encode expected consequences.",
    content: "The move is from romance language to system language: consequences are not exceptions, they are the operating logic.",
  },
  {
    reactionId: 4103,
    type: "retrospect",
    chapterRef: "Chapter 1",
    sectionRef: "1.3",
    anchorQuote: "Relationships are games in the sense that incentives shape what survives.",
    content: "This loops back to the opening claim and turns it into a design principle: incentives explain continuity better than stated intentions do.",
  },
] as const satisfies ReadonlyArray<{
  reactionId: ReactionId;
  type: ReactionType;
  chapterRef: string;
  sectionRef: string;
  anchorQuote: string;
  content: string;
}>;
