from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
)

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

OUTPUT_PDF = BASE_DIR / "Lab7_FuzzTesting_Report_Transit_Fare_Application.pdf"

SCREENSHOTS = {
    "original": "original_processor_output.png",
    "failure_details": "fuzz_tests_failing_details.png",
    "failure_summary": "fuzz_tests_failing_summary.png",
    "fixed": "fixed_processor_output.png",
    "passing": "final_fuzz_tests_passing.png",
}

for name, filename in SCREENSHOTS.items():
    path = SCREENSHOTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing screenshot: {path}")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 0.72 * inch
RIGHT_MARGIN = 0.72 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    alignment=0,
    spaceAfter=9,
))

styles.add(ParagraphStyle(
    name="ProjectTitle",
    parent=styles["Heading2"],
    fontSize=13,
    leading=17,
    spaceAfter=12,
))

styles.add(ParagraphStyle(
    name="SectionHead",
    parent=styles["Heading2"],
    fontSize=11.5,
    leading=14,
    spaceBefore=8,
    spaceAfter=6,
))

styles.add(ParagraphStyle(
    name="BodySmall",
    parent=styles["BodyText"],
    fontSize=9.2,
    leading=13,
    spaceAfter=7,
))

styles.add(ParagraphStyle(
    name="Meta",
    parent=styles["BodyText"],
    fontSize=9.5,
    leading=14,
    spaceAfter=1,
))


def add_screenshot(story, filename, max_height):
    path = SCREENSHOTS_DIR / filename
    img = Image(str(path))
    img._restrictSize(CONTENT_WIDTH, max_height)
    story.append(img)


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        0.32 * inch,
        f"Lab 7 | Page {doc.page}"
    )
    canvas.restoreState()


def build_report():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=RIGHT_MARGIN,
        leftMargin=LEFT_MARGIN,
        topMargin=0.62 * inch,
        bottomMargin=0.58 * inch,
    )

    story = []

    # PAGE 1: Original application execution
    story.extend([
        Paragraph("Lab 7 - Fuzz Testing Report", styles["ReportTitle"]),
        Paragraph(
            "Transit Fare Application | Hypothesis and pytest",
            styles["ProjectTitle"]
        ),
        Paragraph("Name: Aarohi Jaiswal", styles["Meta"]),
        Paragraph("Class: 5A", styles["Meta"]),
        Paragraph("PES1UG24CS009", styles["Meta"]),
        Spacer(1, 10),
        Paragraph(
            "This report documents the original transit fare application "
            "execution, failures discovered through property-based fuzz "
            "testing, the input-validation fixes, and the final test results.",
            styles["BodySmall"]
        ),
        Paragraph(
            "1. Original application execution",
            styles["SectionHead"]
        ),
        Paragraph(
            "The original application was run with valid sample inputs: "
            "DT-UP-3 for the transit corridor, STUDENT for the concession "
            "category, and 50/10.0 for passenger density.",
            styles["BodySmall"]
        ),
    ])

    add_screenshot(
        story, SCREENSHOTS["original"], 4.35 * inch
    )

    # PAGE 2: Initial failures
    story.append(PageBreak())

    story.extend([
        Paragraph(
            "2. Initial Hypothesis failures",
            styles["SectionHead"]
        ),
        Paragraph(
            "The initial fuzz tests exposed failures in all three functions: "
            "<font name='Courier'>parse_transit_corridor</font>, "
            "<font name='Courier'>lookup_concession_discount</font>, and "
            "<font name='Courier'>compute_passenger_density</font>. "
            "Hypothesis generated malformed and missing inputs that caused "
            "the original implementation to raise exceptions.",
            styles["BodySmall"]
        ),
    ])

    add_screenshot(
        story, SCREENSHOTS["failure_details"], 2.85 * inch
    )

    story.extend([
        Spacer(1, 5),
        Paragraph(
            "3. Initial failure summary",
            styles["SectionHead"]
        ),
        Paragraph(
            "The pytest summary confirms that all three initial fuzz-test "
            "functions failed. The detailed output includes minimized "
            "examples such as empty strings, None, and malformed numeric input.",
            styles["BodySmall"]
        ),
    ])

    add_screenshot(
        story, SCREENSHOTS["failure_summary"], 1.55 * inch
    )

    # PAGE 3: Fixed application and final tests
    story.append(PageBreak())

    story.extend([
        Paragraph(
            "4. Fixed application execution",
            styles["SectionHead"]
        ),
        Paragraph(
            "Input validation was added to all three functions. Invalid "
            "corridor codes are handled with an invalid-code message; "
            "unsupported concession categories and invalid passenger-density "
            "inputs are rejected without uncaught exceptions. The application "
            "was then run again with valid sample inputs.",
            styles["BodySmall"]
        ),
    ])

    add_screenshot(
        story, SCREENSHOTS["fixed"], 2.35 * inch
    )

    story.extend([
        Spacer(1, 6),
        Paragraph(
            "5. Final Hypothesis test results",
            styles["SectionHead"]
        ),
        Paragraph(
            "The updated fuzz-test suite completed successfully: "
            "all three tests passed.",
            styles["BodySmall"]
        ),
    ])

    add_screenshot(
        story, SCREENSHOTS["passing"], 2.0 * inch
    )

    story.extend([
        Spacer(1, 7),
        Paragraph(
            "Summary of findings",
            styles["SectionHead"]
        ),
        Paragraph(
            "Hypothesis identified malformed corridor codes, unsupported "
            "concession categories, missing values, and malformed "
            "passenger-to-distance inputs. The application was updated "
            "to validate input types and formats and to handle invalid "
            "values safely. Final verification: 3 tests passed.",
            styles["BodySmall"]
        ),
    ])

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    print(f"PDF created successfully: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_report()
