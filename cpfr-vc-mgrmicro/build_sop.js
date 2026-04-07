/**
 * Build CPFR_VC_Vendor_Info_Manager_SOP.docx from SOP.md using Chewy docx styles.
 *
 * Prerequisites:
 *   The style module (../Chewy Style Template/chewy_docx_style.js) requires the
 *   docx package installed next to it. Run once before building:
 *     cd "../Chewy Style Template" && npm install
 *
 * Usage (from this directory):
 *   node build_sop.js
 *     -- or --
 *   npm run build:sop   (after npm install in this directory too, for the script alias)
 *
 * Output: CPFR_VC_Vendor_Info_Manager_SOP.docx (same directory as SOP.md)
 *
 * IMPORTANT: Document, Packer, Table, TableRow, and WidthType are intentionally
 * loaded from the style template's own node_modules so that every object in the
 * document tree comes from the same docx module instance. Mixing two instances
 * causes Word to see empty paragraphs (rootKey serialization instead of XML).
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// Load the style module first so its node_modules/docx is resolved.
const STYLE_PATH = path.join(__dirname, '..', 'Chewy Style Template', 'chewy_docx_style.js');
const S = require(STYLE_PATH);

// Resolve docx from the style module's own directory so we share one instance.
// Load index.cjs explicitly -- the package.json main points to the UMD browser
// bundle which does not export CJS symbols correctly under Node require().
const DOCX_PATH = path.join(__dirname, '..', 'Chewy Style Template', 'node_modules', 'docx', 'build', 'index.cjs');
const { Document, Packer, Table, TableRow, WidthType } = require(DOCX_PATH);

const SOP_MD = path.join(__dirname, 'SOP.md');
const OUT_DOCX = path.join(__dirname, 'CPFR_VC_Vendor_Info_Manager_SOP.docx');

/** Byline metadata (edit before publishing). */
const DOCUMENT_META = [
  ['Authors:', 'CPFR / Inventory Management (update as needed)'],
  ['Sponsor:', 'Inventory Management leadership (update as needed)'],
  ['Date:', 'April 2026'],
  ['Status:', 'Internal use'],
];

/**
 * Split markdown **bold** segments into docx TextRuns.
 *
 * Args:
 *   line: Single line of text (may include ** markers)
 *
 * Returns:
 *   Array of TextRun-compatible children from the style module
 */
function boldRuns(line) {
  const parts = String(line).split(/\*\*/);
  const out = [];
  for (let i = 0; i < parts.length; i++) {
    if (parts[i] === '') continue;
    if (i % 2 === 1) out.push(S.bold(parts[i]));
    else out.push(S.normal(parts[i]));
  }
  return out.length ? out : [S.normal(line)];
}

/**
 * Return true if a markdown table separator row.
 *
 * Args:
 *   cells: Array of trimmed cell strings
 *
 * Returns:
 *   Whether every cell is only hyphens (markdown pipe-table separator)
 */
function isTableSeparatorRow(cells) {
  return (
    cells.length > 0 &&
    cells.every((c) => /^:?-+:?$/.test((c || '').replace(/\s/g, '')))
  );
}

/**
 * Parse a markdown pipe table starting at lines[startIndex].
 *
 * Args:
 *   lines: All lines of the file
 *   startIndex: Index of first line that starts with |
 *
 * Returns:
 *   { table: Table, nextIndex: number }
 */
function parseTable(lines, startIndex) {
  const rowLines = [];
  let i = startIndex;
  while (i < lines.length) {
    const raw = lines[i].trim();
    if (!raw.startsWith('|')) break;
    rowLines.push(raw);
    i += 1;
  }

  const dataRows = [];
  for (const rl of rowLines) {
    const cells = rl
      .split('|')
      .slice(1, -1)
      .map((c) => c.trim().replace(/\*\*/g, ''));
    if (cells.length && isTableSeparatorRow(cells)) continue;
    dataRows.push(cells);
  }

  const colCount = dataRows.reduce((m, r) => Math.max(m, r.length), 0);
  const unit = Math.floor(S.CONTENT_WIDTH / colCount);
  const columnWidths = Array.from({ length: colCount }, (_, k) =>
    k === colCount - 1 ? S.CONTENT_WIDTH - unit * (colCount - 1) : unit
  );

  const docxRows = dataRows.map((cells, rowIdx) => {
    const padded = cells.slice();
    while (padded.length < colCount) padded.push('');
    const isHeader = rowIdx === 0;
    return new TableRow({
      children: padded.map((text, ci) => {
        const w = columnWidths[ci];
        if (isHeader) return S.headerCell(text, w);
        return S.cell(text, { width: w });
      }),
    });
  });

  const table = new Table({
    width: { size: S.CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths,
    rows: docxRows,
  });

  return { table, nextIndex: i };
}

/**
 * Parse markdown body (no leading H1) into docx children.
 *
 * Args:
 *   md: Markdown string
 *
 * Returns:
 *   Array of Paragraph | Table elements
 */
function parseMarkdownBody(md) {
  const lines = md.split(/\r?\n/);
  const children = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const t = line.trim();

    if (t === '' || t === '---') {
      i += 1;
      continue;
    }

    if (t.startsWith('### ')) {
      children.push(S.h3(t.slice(4)));
      i += 1;
      continue;
    }

    if (t.startsWith('## ')) {
      children.push(S.h2(t.slice(3)));
      i += 1;
      continue;
    }

    if (t.startsWith('|')) {
      const { table, nextIndex } = parseTable(lines, i);
      children.push(table);
      i = nextIndex;
      continue;
    }

    if (t.startsWith('- ')) {
      children.push(S.bullet1(boldRuns(t.slice(2))));
      i += 1;
      continue;
    }

    if (t.startsWith('*') && t.endsWith('*') && t.length > 2 && !t.startsWith('**')) {
      children.push(S.bodyPara([S.italic(t.slice(1, -1))]));
      i += 1;
      continue;
    }

    const paraLines = [];
    while (i < lines.length) {
      const L = lines[i];
      const u = L.trim();
      if (u === '' || u === '---') break;
      if (
        u.startsWith('## ') ||
        u.startsWith('### ') ||
        u.startsWith('|') ||
        u.startsWith('- ') ||
        (u.startsWith('*') && u.endsWith('*') && u.length > 2 && !u.startsWith('**'))
      ) {
        break;
      }
      paraLines.push(L.trimEnd());
      i += 1;
    }
    const joined = paraLines.join(' ').trim();
    if (joined) children.push(S.bodyPara(boldRuns(joined)));
  }

  return children;
}

/**
 * Split file content into title (first H1 text) and body markdown.
 *
 * Args:
 *   md: Full file string
 *
 * Returns:
 *   { title: string, body: string }
 */
function extractTitleAndBody(md) {
  const lines = md.split(/\r?\n/);
  if (!lines.length) return { title: 'SOP', body: md };
  const first = lines[0].trim();
  let title = 'SOP';
  let start = 0;
  if (first.startsWith('# ')) {
    title = first.slice(2).trim();
    start = 1;
  }
  while (start < lines.length && lines[start].trim() === '') start += 1;
  const body = lines.slice(start).join('\n');
  return { title, body };
}

function metaTable() {
  return new Table({
    width: { size: S.CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [1800, S.CONTENT_WIDTH - 1800],
    rows: DOCUMENT_META.map(([k, v]) => S.metaRow(k, v)),
  });
}

function buildDocument() {
  const md = fs.readFileSync(SOP_MD, 'utf8');
  const { title, body } = extractTitleAndBody(md);

  const children = [S.h1(title), metaTable(), ...parseMarkdownBody(body)];

  return new Document({
    numbering: S.docNumbering(),
    styles: S.docStyles(),
    sections: [
      {
        properties: S.docPageProps(),
        headers: {
          default: S.docHeader(
            'CPFR VC Vendor Info Manager -- SOP',
            'Internal -- April 2026'
          ),
        },
        footers: { default: S.docFooter() },
        children,
      },
    ],
  });
}

function main() {
  if (!fs.existsSync(SOP_MD)) {
    console.error('Missing SOP.md at', SOP_MD);
    process.exit(1);
  }
  if (!fs.existsSync(STYLE_PATH)) {
    console.error('Missing style module at', STYLE_PATH);
    process.exit(1);
  }

  const doc = buildDocument();
  Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(OUT_DOCX, buf);
    console.log('Wrote', OUT_DOCX);
  }).catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

main();
