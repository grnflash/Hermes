/**
 * CHEWY PROJECT — CANONICAL DOCX STYLE MODULE
 * ─────────────────────────────────────────────────────────────────────────────
 * Reusable style constants and paragraph/table helper functions for all
 * programmatically-generated Word documents in the CPFR/VC/CPH project.
 *
 * USAGE IN A BUILD SCRIPT:
 *   const S = require('./chewy_docx_style');
 *   // Then use S.h2("Section Title"), S.bodyPara("text"), S.cell("value", {...}), etc.
 *   // Pass S.docStyles(), S.docNumbering(), S.docPageProps() into the Document constructor.
 *
 * FONT NOTE:
 *   Primary font is Aptos (Microsoft 365, 2023+). If Aptos is unavailable,
 *   Word will substitute Arial automatically. No action needed on Mac + Word 365.
 *
 * CONTENT WIDTH:
 *   Page 8.5" − left 0.5" − right 0.5" − gutter 0.2" = 10,512 DXA
 *   All table columnWidths arrays must sum to CONTENT_WIDTH (10512).
 *
 * VERSION: 1.0 — locked from CPFR_VC_CPH_Roadmap_v0.4 (2026-03-17)
 * ─────────────────────────────────────────────────────────────────────────────
 */

'use strict';

const {
  Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat, LineRuleType
} = require('docx');

// ─────────────────────────────────────────────
// TYPOGRAPHY CONSTANTS
// ─────────────────────────────────────────────
const FONT          = "Aptos";
const BODY_SIZE     = 20;   // 10pt  (docx half-points)
const BYLINE_SIZE   = 18;   // 9pt   — Authors/Sponsor/Date/Status block only
const H1_SIZE       = 28;   // 14pt  — document title, used once, no border
const H2_SIZE       = 28;   // 14pt  — section headings, top border
const H3_SIZE       = 24;   // 12pt  — sub-section headings, bold italic
const H4_SIZE       = 20;   // 10pt  — sub-sub-section headings, bold

// Line spacing: "Multiple 1.1"  (1.1 × 240 = 264 in docx units)
const LINE_RULE     = LineRuleType.MULTIPLE;
const LINE_VAL      = 264;

// ─────────────────────────────────────────────
// PAGE LAYOUT  (DXA: 1440 = 1 inch)
// ─────────────────────────────────────────────
const PAGE_WIDTH    = 12240;  // 8.5"
const PAGE_HEIGHT   = 15840;  // 11"
const CONTENT_WIDTH = 10512;  // page − left − right − gutter

const PAGE_MARGINS = {
  top:    720,   // 0.5"
  bottom: 720,   // 0.5"
  left:   720,   // 0.5"
  right:  720,   // 0.5"
  gutter: 288,   // 0.2" — accommodates line numbers
  header: 288,   // 0.2" from top edge
  footer: 288,   // 0.2" from bottom edge
};

// ─────────────────────────────────────────────
// COLOR PALETTE
// ─────────────────────────────────────────────
const COLOR = {
  black:        "000000",
  grey75:       "BFBFBF",   // table borders, header/footer rules, line numbers
  greyHeader:   "D9D9D9",   // table header row fill
  white:        "FFFFFF",
  green:        "E2EFDA",   // status: on track / active
  red:          "FCE4D6",   // status: blocked
  yellow:       "FFF2CC",   // status: pending / at risk
};

// ─────────────────────────────────────────────
// TABLE COLUMN PRESETS  (must sum to CONTENT_WIDTH = 10512)
// ─────────────────────────────────────────────
const COLS = {
  T4_DEPENDENCY: [3200, 2600, 2000, 2712],   // Action / Depends On / Owner / Status
  T3_STANDARD:   [3800, 3356, 3356],          // 3-col equal-ish
  T3_LOE:        [3800, 3012, 3700],          // LOE table
  T2_COMPARE:    [2200, 4156, 4156],          // Label / Col A / Col B
};

// ─────────────────────────────────────────────
// INTERNAL PRIMITIVES
// ─────────────────────────────────────────────
const _tableBorder  = { style: BorderStyle.SINGLE, size: 4, color: COLOR.grey75 };
const _allBorders   = { top: _tableBorder, bottom: _tableBorder, left: _tableBorder, right: _tableBorder };
const _noBorders    = {
  top:    { style: BorderStyle.NONE, size: 0, color: COLOR.white },
  bottom: { style: BorderStyle.NONE, size: 0, color: COLOR.white },
  left:   { style: BorderStyle.NONE, size: 0, color: COLOR.white },
  right:  { style: BorderStyle.NONE, size: 0, color: COLOR.white },
};
const _cellPad      = { top: 58, bottom: 58, left: 100, right: 100 };   // ~0.04" top/bottom
const _cellPadZero  = { top: 0,  bottom: 0,  left: 100, right: 100 };   // for byline table
const _sp           = (before, after) => ({ line: LINE_VAL, lineRule: LINE_RULE, before, after });

// ─────────────────────────────────────────────
// TEXT RUN HELPERS
// ─────────────────────────────────────────────
function run(text, opts = {})  { return new TextRun({ text, font: FONT, size: BODY_SIZE, ...opts }); }
function bold(text)            { return run(text, { bold: true }); }
function italic(text)          { return run(text, { italics: true }); }
function normal(text)          { return run(text); }
function boldItalic(text)      { return run(text, { bold: true, italics: true }); }
function bylineRun(text)       { return new TextRun({ text, font: FONT, size: BYLINE_SIZE }); }
function bylineBold(text)      { return new TextRun({ text, font: FONT, size: BYLINE_SIZE, bold: true }); }

// ─────────────────────────────────────────────
// PARAGRAPH HELPERS
// ─────────────────────────────────────────────

/** Standard body paragraph. 6pt before / 6pt after. */
function bodyPara(children, opts = {}) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    children: c,
    spacing: _sp(120, 120),
    ...opts
  });
}

/** Document title — H1. 14pt bold, no border, left-aligned. Used once per document. 6pt/12pt. */
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text, font: FONT, size: H1_SIZE, bold: true })],
    spacing: _sp(120, 240),
  });
}

/** Section heading — H2. 14pt bold, 1.5pt top border, 4pt border-text gap. 18pt/9pt. */
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: FONT, size: H2_SIZE, bold: true })],
    spacing: _sp(360, 180),
    border: { top: { style: BorderStyle.SINGLE, size: 12, color: COLOR.black, space: 4 } },
  });
}

/** Sub-section heading — H3. 12pt bold italic. 6pt/6pt. */
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, font: FONT, size: H3_SIZE, bold: true, italics: true })],
    spacing: _sp(120, 120),
  });
}

/** Sub-sub-section heading — H4. 10pt bold. 6pt/6pt. */
function h4(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_4,
    children: [new TextRun({ text, font: FONT, size: H4_SIZE, bold: true })],
    spacing: _sp(120, 120),
  });
}

/** Level-1 bullet. Filled circle •. Aligned 0.1" / indent 0.25". 6pt/6pt. */
function bullet1(children) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: c,
    spacing: _sp(120, 120),
  });
}

/** Level-2 bullet. Open circle ○. Aligned 0.25" / indent 0.4". 6pt/6pt. */
function bullet2(children) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    numbering: { reference: "bullets", level: 1 },
    children: c,
    spacing: _sp(120, 120),
  });
}

/** Level-1 numbered list item. */
function num1(children) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    numbering: { reference: "numbered", level: 0 },
    children: c,
    spacing: _sp(120, 120),
  });
}

/** Level-2 numbered list item (alpha). */
function num2(children) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    numbering: { reference: "numbered", level: 1 },
    children: c,
    spacing: _sp(120, 120),
  });
}

/** Level-3 numbered list item (roman). */
function num3(children) {
  const c = typeof children === 'string' ? [run(children)] : children;
  return new Paragraph({
    numbering: { reference: "numbered", level: 2 },
    children: c,
    spacing: _sp(120, 120),
  });
}

// ─────────────────────────────────────────────
// TABLE HELPERS
// ─────────────────────────────────────────────

/** Standard table header cell. Light grey fill, 10pt bold. */
function headerCell(text, width) {
  return new TableCell({
    borders: _allBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLOR.greyHeader, type: ShadingType.CLEAR },
    margins: _cellPad,
    children: [new Paragraph({
      children: [new TextRun({ text, font: FONT, size: BODY_SIZE, bold: true })],
      spacing: _sp(0, 0),
    })]
  });
}

/**
 * Standard table body cell.
 * opts: { width, shade, bold, italic }
 * shade: use COLOR.green / COLOR.red / COLOR.yellow for status cells.
 */
function cell(text, opts = {}) {
  const { shade, bold: isBold, italic: isItalic, width = 2000 } = opts;
  return new TableCell({
    borders: _allBorders,
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    margins: _cellPad,
    children: [new Paragraph({
      children: [new TextRun({ text, font: FONT, size: BODY_SIZE, bold: !!isBold, italics: !!isItalic })],
      spacing: _sp(0, 0),
    })]
  });
}

/**
 * Byline table row (Authors / Sponsor / Date / Status block).
 * Borderless, 9pt, 0pt before/after. Used in the document header metadata table only.
 */
function metaRow(label, value) {
  return new TableRow({ children: [
    new TableCell({
      borders: _noBorders,
      width: { size: 1800, type: WidthType.DXA },
      margins: _cellPadZero,
      children: [new Paragraph({ style: "BodyText2", spacing: _sp(0, 0), children: [bylineBold(label)] })]
    }),
    new TableCell({
      borders: _noBorders,
      width: { size: CONTENT_WIDTH - 1800, type: WidthType.DXA },
      margins: _cellPadZero,
      children: [new Paragraph({ style: "BodyText2", spacing: _sp(0, 0), children: [bylineRun(value)] })]
    }),
  ]});
}

// ─────────────────────────────────────────────
// DOCUMENT-LEVEL CONFIG BLOCKS
// Pass these into the Document({}) constructor.
// ─────────────────────────────────────────────

/** Numbering config block — pass as Document({ numbering: docNumbering() }) */
function docNumbering() {
  return {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: {
              paragraph: { indent: { left: 360, hanging: 216 }, spacing: _sp(120, 120) },
              run: { font: FONT, size: BODY_SIZE }
            }
          },
          {
            level: 1, format: LevelFormat.BULLET, text: "\u25CB", alignment: AlignmentType.LEFT,
            style: {
              paragraph: { indent: { left: 576, hanging: 216 }, spacing: _sp(120, 120) },
              run: { font: FONT, size: BODY_SIZE }
            }
          },
        ]
      },
      {
        reference: "numbered",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL,      text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 360, hanging: 216 }, spacing: _sp(120, 120) }, run: { font: FONT, size: BODY_SIZE } } },
          { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 576, hanging: 216 }, spacing: _sp(120, 120) }, run: { font: FONT, size: BODY_SIZE } } },
          { level: 2, format: LevelFormat.LOWER_ROMAN,  text: "%3.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 792, hanging: 216 }, spacing: _sp(120, 120) }, run: { font: FONT, size: BODY_SIZE } } },
        ]
      },
    ]
  };
}

/** Styles config block — pass as Document({ styles: docStyles() }) */
function docStyles() {
  return {
    default: {
      document: { run: { font: FONT, size: BODY_SIZE } },
      paragraph: { spacing: _sp(120, 120) },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: H1_SIZE, bold: true, color: COLOR.black },
        paragraph: { spacing: _sp(120, 240), outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: H2_SIZE, bold: true, color: COLOR.black },
        paragraph: {
          spacing: _sp(360, 180),
          border: { top: { style: BorderStyle.SINGLE, size: 12, color: COLOR.black, space: 4 } },
          outlineLevel: 1
        }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: H3_SIZE, bold: true, italics: true, color: COLOR.black },
        paragraph: { spacing: _sp(120, 120), outlineLevel: 2 }
      },
      {
        id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: H4_SIZE, bold: true, color: COLOR.black },
        paragraph: { spacing: _sp(120, 120), outlineLevel: 3 }
      },
      {
        id: "BodyText2", name: "Body Text 2", basedOn: "Normal", next: "Normal", quickFormat: false,
        run: { font: FONT, size: BYLINE_SIZE, color: COLOR.black },
        paragraph: { spacing: _sp(0, 0) }
      },
    ]
  };
}

/**
 * Section properties block — pass as the properties key inside a section.
 * Includes page size, margins, and line numbering.
 * Usage: sections: [{ properties: docPageProps(), headers: {...}, children: [...] }]
 */
function docPageProps() {
  return {
    page: {
      size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
      margin: PAGE_MARGINS,
    },
    lineNumbers: {
      countBy: 1,
      restart: "newPage",
      distance: 360,
    },
  };
}

/**
 * Standard document header. Pass docTitle and draftLabel (e.g. "Draft v0.4 — Internal Review").
 * Usage: headers: { default: docHeader("My Title", "Draft v1.0") }
 */
function docHeader(docTitle, draftLabel) {
  return new Header({
    children: [new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COLOR.grey75, space: 2 } },
      spacing: { before: 0, after: 60 },
      children: [
        new TextRun({ text: docTitle, font: FONT, size: 16, color: "808080" }),
        new TextRun({ text: "\t" + draftLabel, font: FONT, size: 16, color: "808080" }),
      ],
      tabStops: [{ type: "right", position: CONTENT_WIDTH }]
    })]
  });
}

/**
 * Standard document footer. Pass confidentiality label (default: "Confidential — Internal Use Only").
 * Usage: footers: { default: docFooter() }
 */
function docFooter(label = "Confidential \u2014 Internal Use Only") {
  return new Footer({
    children: [new Paragraph({
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: COLOR.grey75, space: 2 } },
      spacing: { before: 60, after: 0 },
      children: [
        new TextRun({ text: label, font: FONT, size: 16, color: "808080" }),
        new TextRun({ text: "\tPage ", font: FONT, size: 16, color: "808080" }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "808080" }),
      ],
      tabStops: [{ type: "right", position: CONTENT_WIDTH }]
    })]
  });
}

// ─────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────
module.exports = {
  // Constants (useful for custom column width calculations)
  FONT, BODY_SIZE, BYLINE_SIZE, H1_SIZE, H2_SIZE, H3_SIZE, H4_SIZE,
  CONTENT_WIDTH, PAGE_MARGINS, COLOR, COLS,

  // Text run helpers
  run, bold, italic, normal, boldItalic, bylineRun, bylineBold,

  // Paragraph helpers
  bodyPara, h1, h2, h3, h4,
  bullet1, bullet2, num1, num2, num3,

  // Table helpers
  headerCell, cell, metaRow,

  // Document config blocks
  docNumbering, docStyles, docPageProps, docHeader, docFooter,
};
