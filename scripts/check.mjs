#!/usr/bin/env node
// Verifies the distillation layers (openspec/specs/distillation/spec.md):
//   - every lesson's front matter is complete and valid, and its sources exist;
//   - the notes manifest is valid JSONL (bad lines are warnings, not failures);
//   - the generated files are current (the build is re-run in memory and
//     compared byte for byte with what is on disk);
//   - notes and lessons hold nothing that looks like a secret or a host path.
// Exits non-zero on any failure.
//
// Usage: node scripts/check.mjs

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT, build, staleOutputs, formatProblem } from './build.mjs';

const failures = [];
const warnings = [];

// 1. Lessons and manifest, as the build sees them.
const { files, lessons, notes, problems } = build();
for (const p of problems) (p.level === 'error' ? failures : warnings).push(formatProblem(p));

// 2. Generated files are up to date.
for (const [rel, content] of files) {
  const path = join(ROOT, rel);
  if (!existsSync(path)) failures.push(`ERROR ${rel}: missing; run node scripts/build.mjs`);
  else if (readFileSync(path, 'utf8') !== content) failures.push(`ERROR ${rel}: out of date; run node scripts/build.mjs`);
}
for (const rel of staleOutputs(files)) failures.push(`ERROR ${rel}: generated page has no lesson source; run node scripts/build.mjs to remove it`);

// 3. Public-safety scan over notes and lessons.
const SECRETS = [
  [/(?<![\w.:/~-])\/(?:home|run|root|Users)\/[\w.-]/, 'a host path'],
  [/\bgh[pousr]_[A-Za-z0-9]{10,}/, 'a GitHub token (ghp_ and friends)'],
  [/\bgithub_pat_[A-Za-z0-9_]{10,}/, 'a GitHub fine-grained token'],
  [/\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{16,}/, 'an API key (sk-...)'],
  [/\bAKIA[0-9A-Z]{16}\b/, 'an AWS access key id'],
  [/\bxox[abposr]-[A-Za-z0-9-]{10,}/, 'a Slack token'],
  [/\bAIza[0-9A-Za-z_-]{35}\b/, 'a Google API key'],
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----|BEGIN PRIVATE KEY/, 'a private key'],
  [/\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/, 'a JWT'],
  [/\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["']?[A-Za-z0-9_\-/+]{12,}/i, 'a credential assignment'],
];
const scanTargets = [];
for (const dir of ['public/notes', 'public/lessons']) {
  const abs = join(ROOT, dir);
  if (!existsSync(abs)) continue;
  for (const f of readdirSync(abs).sort()) if (/\.(md|jsonl)$/.test(f)) scanTargets.push(`${dir}/${f}`);
}
for (const rel of scanTargets) {
  readFileSync(join(ROOT, rel), 'utf8').split('\n').forEach((line, i) => {
    for (const [re, what] of SECRETS) {
      if (re.test(line)) failures.push(`ERROR ${rel}:${i + 1}: looks like ${what}; the site is public, remove it`);
    }
  });
}

for (const w of warnings) console.log(w);
for (const f of failures) console.log(f);
console.log(`checked ${lessons.length} lesson(s), ${notes.length} note(s), ${files.size} generated file(s), ${scanTargets.length} file(s) scanned for secrets: ${failures.length} error(s), ${warnings.length} warning(s)`);
if (failures.length) { console.log('check FAILED'); process.exit(1); }
console.log('check passed');
