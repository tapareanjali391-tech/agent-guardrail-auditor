#!/usr/bin/env python3
"""Generate work-sample-summary.pdf for AI safety fellowship application."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).parent / "work-sample-summary.pdf"
GITHUB = "https://github.com/tapareanjali391-tech/agent-guardrail-auditor"

ARCHITECTURE = """  Incoming Context (web pages, tool outputs, documents)
                          |
                          v
               +----------------------+
               | PromptInjectionDet.  |---> quarantine suspicious content
               +----------+-----------+
                          | clean content only
                          v
                    +-----------+
                    |   Agent   |
                    +-----+-----+
                          | proposes action
                          v
               +---------------------+
               |   ActionAuditor     |
               |   Policy Check      |
               +----------+----------+
                          v
           ALLOW  |  BLOCK  |  ESCALATE_TO_HUMAN
                          |
                          v
                   audit_log.json"""


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
        ),
        "link": ParagraphStyle(
            "Link",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0366d6"),
            spaceAfter=14,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor("#111111"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            leftIndent=14,
            bulletIndent=4,
            spaceAfter=3,
        ),
        "mono": ParagraphStyle(
            "Mono",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.2,
            leading=8.5,
            spaceAfter=4,
        ),
    }


def demo_table():
    data = [
        ["Scenario", "Verdict"],
        ["Read job posting", "ALLOW"],
        ["Fabricated experience in application", "BLOCK"],
        ["Honest application submission", "ESCALATE_TO_HUMAN"],
        ["4th submission within an hour (rate limit)", "ESCALATE_TO_HUMAN"],
        ["Premium purchase attempt", "BLOCK"],
        ["Injected prompt in scraped HTML", "QUARANTINED"],
    ]
    table = Table(data, colWidths=[4.2 * inch, 1.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def architecture_block(styles):
    """Render flow diagram inside a bordered box."""
    inner = Preformatted(ARCHITECTURE, styles["mono"])
    outer = Table([[inner]], colWidths=[6.0 * inch])
    outer.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cccccc")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return outer


def main():
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Agent Guardrail Auditor — Work Sample Summary",
        author="Agent Guardrail Auditor",
    )

    story = [
        Paragraph("Agent Guardrail Auditor", styles["title"]),
        Paragraph(
            "A safety framework for auditing autonomous LLM agent actions",
            styles["subtitle"],
        ),
        Paragraph(
            f'<a href="{GITHUB}" color="#0366d6">{GITHUB}</a>',
            styles["link"],
        ),
        Paragraph("Motivation", styles["heading"]),
        Paragraph(
            "As LLM agents gain the ability to take autonomous real-world actions — "
            "browsing websites, submitting forms, making purchases, and sending "
            "communications — the cost of an unchecked mistake scales with every step "
            "the agent takes without oversight. A single runaway loop can spam "
            "applications, spend money, or leak credentials before a human notices. "
            "This project wraps an agent's action loop with programmatic guardrails: "
            "every proposed action is evaluated against authored safety policies before "
            "execution, and untrusted context is scanned for prompt-injection attempts "
            "before it reaches the agent.",
            styles["body"],
        ),
        Paragraph("Architecture", styles["heading"]),
        architecture_block(styles),
        Spacer(1, 6),
        Paragraph("Demo Results", styles["heading"]),
        demo_table(),
        Spacer(1, 6),
        Paragraph("Relevance to AI Safety Research", styles["heading"]),
        Paragraph(
            "This project is a practical engineering exploration of problems central to "
            "AI safety research: <b>scalable oversight</b> (automating routine policy "
            "checks while routing high-risk decisions to humans), <b>corrigibility</b> "
            "(explicit BLOCK and ESCALATE verdicts create intervention points before "
            "irreversible actions), and <b>defense against prompt injection</b> "
            "(quarantining hijack attempts in untrusted retrieved content). It "
            "demonstrates how lightweight guardrails can be layered onto agentic systems "
            "today, while surfacing the gaps that production deployments must address.",
            styles["body"],
        ),
        Paragraph("Limitations &amp; Future Work", styles["heading"]),
        Paragraph(
            "• Rule-based pattern matching rather than learned classification",
            styles["bullet"],
        ),
        Paragraph(
            "• Policies must be manually authored and may miss novel attack patterns",
            styles["bullet"],
        ),
        Paragraph(
            "• Prompt-injection detection relies on regex heuristics, evadable by adversaries",
            styles["bullet"],
        ),
        Paragraph(
            "• Production use would require adversarial red-teaming and likely a "
            "fine-tuned classifier for injection detection",
            styles["bullet"],
        ),
    ]

    doc.build(story)
    print(f"Created: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
