import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

// People: one Markdown file per person in src/content/people/.
// role: pi | postdoc | phd | ms | visiting | ug | alumni
const people = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/people' }),
  schema: z.object({
    name: z.string(),
    name_ko: z.string().optional(),
    role: z.enum(['pi', 'postdoc', 'phd', 'ms', 'visiting', 'ug', 'alumni']),
    title: z.string(),
    affiliation: z.string().optional(),
    email: z.string().optional(),
    photo: z.string().optional(),          // file name in public/img/people/
    website: z.string().optional(),
    scholar: z.string().optional(),
    github: z.string().optional(),
    linkedin: z.string().optional(),
    start: z.string().optional(),          // YYYY-MM
    end: z.string().optional(),            // YYYY-MM (alumni)
    next_position: z.string().optional(),  // alumni
    order: z.number().default(0),          // smaller shows first within a section
    education: z
      .array(z.object({ degree: z.string(), school: z.string(), dept: z.string().optional(), year: z.string().optional() }))
      .default([]),
  }),
});

// News: one Markdown file per item in src/content/news/. The body is the text.
const news = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/news' }),
  schema: z.object({
    date: z.coerce.date(),
    title: z.string().optional(),   // optional headline; short items can leave it out
    draft: z.boolean().default(false),
    paper: z.string().optional(),   // DOI of the paper this item announces (written by the paper check)
  }),
});

// Research areas: one Markdown file per area in src/content/research/.
const research = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/research' }),
  schema: z.object({
    title: z.string(),
    order: z.number(),
    question: z.string(),
    methods: z.array(z.string()).default([]),
    papers: z.array(z.string()).default([]),   // DOIs or BibTeX keys from papers.bib
    image: z.string().optional(),              // e.g. /img/research/area1.png ; if absent a schematic is drawn
    figure: z.string().optional(),             // name of the built-in schematic
  }),
});

// Teaching: src/data/teaching.yaml
const teaching = defineCollection({
  loader: file('src/data/teaching.yaml'),
  schema: z.object({
    term: z.string(),
    term_order: z.number(),
    title: z.string(),
    title_ko: z.string().optional(),
    code: z.string().optional(),
    level: z.string().optional(),
    unit: z.string().optional(),
    schedule: z.string().optional(),
    description: z.string().optional(),
  }),
});

export const collections = { people, news, research, teaching };
