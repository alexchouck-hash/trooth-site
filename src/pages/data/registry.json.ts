/**
 * /data/registry.json - the feed directory as a file.
 *
 * The directory page is a rendering of this artifact, not a separate copy of it, and the point of
 * serving the raw file is that a reader never has to scrape the table to get what the table shows.
 * It is the same JSON generated in the Trooth repo by jobs/site_data.py and copied into src/data
 * at publish time, returned verbatim.
 */
import registry from '../../data/registry.json';

export function GET() {
  return new Response(JSON.stringify(registry), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
}
