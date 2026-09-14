/**
 * Where Modafied lives, and nothing else.
 *
 * Trooth deliberately keeps no copy of a Modafied grade. Everything about a Modafied measurement
 * is fetched from Modafied at view time by its own embed script, so the claim on any Trooth page
 * is whatever the benchmark currently publishes, not whatever we last copied down.
 *
 * Trooth funds Modafied. That is the reason for the strictness, not an exception to it: a funder
 * caching a funder-flattering grade is indistinguishable from a funder editing it.
 *
 * modafied.org is the intended home, but its DNS does not resolve yet, so this points at where
 * the benchmark is actually served today. One constant to change when the domain goes live.
 */
export const MODAFIED_ORIGIN = "https://alexchouck-hash.github.io/modafied-site";

export const MODAFIED_EMBED_SRC = `${MODAFIED_ORIGIN}/v1/embed.js`;

/** Modafied's own page for a subject, for links we render ourselves. */
export function modafiedCardUrl(subjectId: string): string {
  return `${MODAFIED_ORIGIN}/scorecards/${subjectId}`;
}

/** Modafied's trace resolver, where an emblem's id is turned back into its evidence. */
export const MODAFIED_TRACE_URL = `${MODAFIED_ORIGIN}/trace/`;
export const MODAFIED_METHOD_URL = `${MODAFIED_ORIGIN}/method/`;
