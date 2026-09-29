// Reads src/data/papers.bib and turns it into plain objects for the pages.
// To add a paper, add a BibTeX entry to papers.bib. Useful optional fields:
//   selected = {true}      -> shown under "Selected" and on the home page
//   arxiv = {2602.16636}   -> adds an arXiv link
//   status = {under review} or journal = {Under review} -> listed under "Under review"
//   cofirst = {1,2}         -> authors 1 and 2 marked * (equal contribution)
//   cocorresponding = {2,3} -> authors 2 and 3 marked † (co-corresponding)
//   preview = {name.jpg}    -> figure shown next to the paper (file in public/img/papers/)
import fs from 'node:fs';
import path from 'node:path';
import { parse } from '@retorquere/bibtex-parser';

export type Paper = {
  key: string;
  title: string;
  authors: { first: string; last: string; isPI: boolean; cofirst: boolean; cocorr: boolean }[];
  journal: string;
  year: number;
  volume?: string;
  number?: string;
  pages?: string;
  doi?: string;
  arxiv?: string;
  url?: string;
  preview?: string;
  selected: boolean;
  underReview: boolean;
  bibtex: string;
};

// Fields that are for the website or a reference manager only; they are removed from the BibTeX shown to visitors.
const HIDDEN_FIELDS = [
  'abstract', 'keywords', 'local-url', 'google_scholar_id', 'altmetric', 'dimensions', 'selected',
  'preview', 'status', 'pmid', 'pmcid', 'issn', 'annotation', 'file', 'cofirst', 'cocorresponding',
];

const PI_LAST = 'Jun';
const PI_FIRST = /^kyu-?jung$/i;

function cleanBibtex(raw: string): string {
  const lines = raw.trim().split('\n');
  const out: string[] = [];
  let skipping = false;
  let depth = 0;
  for (const line of lines) {
    if (!skipping) {
      const m = line.match(/^\s*([A-Za-z_-]+)\s*=/);
      if (m && HIDDEN_FIELDS.includes(m[1].toLowerCase())) {
        depth = (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
        skipping = depth > 0;
        continue;
      }
      out.push(line.replace(/\s+$/, ''));
    } else {
      depth += (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
      if (depth <= 0) skipping = false;
    }
  }
  // make sure the last field line does not end with a dangling comma before the closing brace
  const text = out.join('\n').replace(/,\s*\n\}$/, '\n}');
  return text;
}

let cache: Paper[] | null = null;

export function getPapers(): Paper[] {
  if (cache) return cache;
  const file = path.join(process.cwd(), 'src/data/papers.bib');
  const lib = parse(fs.readFileSync(file, 'utf8'), {
    sentenceCase: false,
    english: false,
    unsupported: 'ignore',
  });
  if (lib.errors.length) {
    console.warn('[papers.bib] parse problems:', lib.errors.map((e) => e.error));
  }
  const papers: Paper[] = lib.entries.map((e) => {
    const f = e.fields as Record<string, any>;
    const idx = (v: any) => new Set(String(v || '').split(/[,\s]+/).filter(Boolean).map((x) => parseInt(x, 10)));
    const cf = idx(f.cofirst), cc = idx(f.cocorresponding);
    const authors = (f.author || []).map((a: any, i: number) => {
      const first = (a.firstName || '').trim();
      const last = (a.lastName || a.name || '').trim();
      return { first, last, isPI: last === PI_LAST && PI_FIRST.test(first.replace(/\s/g, '')), cofirst: cf.has(i + 1), cocorr: cc.has(i + 1) };
    });
    const journal = (f.journal || f.booktitle || '').trim();
    const status = String(f.status || '').toLowerCase();
    const doi = f.doi ? String(f.doi).trim() : undefined;
    return {
      key: e.key,
      title: String(f.title || '').replace(/[{}]/g, '').trim(),
      authors,
      journal,
      year: parseInt(f.year, 10) || 0,
      volume: f.volume,
      number: f.number,
      pages: f.pages,
      doi,
      arxiv: f.arxiv || f.eprint || (doi?.toLowerCase().includes('arxiv.') ? doi.split('arxiv.').pop() : undefined),
      url: f.url,
      preview: f.preview ? String(f.preview).trim() : undefined,
      selected: String(f.selected).toLowerCase() === 'true',
      underReview: status.includes('review') || /under review|in preparation|submitted/i.test(journal),
      bibtex: cleanBibtex(e.input),
    };
  });
  papers.sort((a, b) => b.year - a.year);
  cache = papers;
  return papers;
}

export function paperByDoiOrKey(id: string): Paper | undefined {
  const k = id.toLowerCase();
  return getPapers().find((p) => p.key.toLowerCase() === k || p.doi?.toLowerCase() === k);
}

export function formatAuthor(a: Paper['authors'][number]): string {
  return a.first ? `${a.first} ${a.last}` : a.last;
}
