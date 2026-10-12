const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, PageBreak,
  TabStopType, TabStopPosition
} = require('docx');
const fs = require('fs');

const BLUE = "1F4E79";
const LIGHT_BLUE = "D6E4F0";
const MID_BLUE = "2E75B6";
const WHITE = "FFFFFF";
const DARK = "1A1A1A";
const GRAY_BG = "F2F2F2";

const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: MID_BLUE, space: 4 } },
    children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: BLUE })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 100 },
    children: [new TextRun({ text, font: "Arial", size: 24, bold: true, color: MID_BLUE })]
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 180, after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: BLUE })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    alignment: opts.center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, font: "Arial", size: 20, bold: opts.bold || false, color: opts.color || DARK })]
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: DARK })]
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: DARK })]
  });
}

function spacer(lines = 1) {
  return new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "", size: lines * 10 })] });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function sectionBanner(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: noBorders,
            shading: { fill: BLUE, type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 200, right: 200 },
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text, font: "Arial", size: 24, bold: true, color: WHITE })]
            })]
          })
        ]
      })
    ]
  });
}

function headerTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3120, 6240],
    rows: rows.map(([label, value]) => new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          width: { size: 3120, type: WidthType.DXA },
          shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: label, font: "Arial", size: 20, bold: true, color: BLUE })] })]
        }),
        new TableCell({
          borders: noBorders,
          width: { size: 6240, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: value, font: "Arial", size: 20, color: DARK })] })]
        })
      ]
    }))
  });
}

function milestoneTable() {
  const headers = ["Milestone", "Working Day", "Date", "Deliverables", "Payment %", "Amount (USD)"];
  const colWidths = [1700, 900, 1200, 2760, 900, 900];
  const data = [
    ["M1: Contract Signing", "Day 0", "Feb 24, 2026", "Contract signed, project kickoff, requirements finalization", "30%", "$4,350.00"],
    ["M2: Phase 1 Complete", "Day 14", "Mar 12, 2026", "Backend development, database setup, authentication, core APIs", "20%", "$2,900.00"],
    ["M3: Phase 2 Complete", "Day 23", "Mar 26, 2026", "Operations dashboards, fleet management, driver management", "20%", "$2,900.00"],
    ["M4: Phase 3 Complete", "Day 32", "Apr 9, 2026", "AI customer service, collection automation, integrations", "20%", "$2,900.00"],
    ["M5: Final Delivery", "Day 45", "Apr 30, 2026", "Testing, deployment, training, go-live support", "10%", "$1,450.00"],
    ["TOTAL", "", "", "", "100%", "$14,500.00"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 100, right: 100 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...data.map((row, ri) => new TableRow({
        children: row.map((cell, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: ri === data.length - 1 ? LIGHT_BLUE : (ri % 2 === 0 ? WHITE : GRAY_BG), type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          children: [new Paragraph({
            alignment: i === 4 || i === 5 ? AlignmentType.CENTER : AlignmentType.LEFT,
            children: [new TextRun({ text: cell, font: "Arial", size: ri === data.length - 1 ? 20 : 18, bold: ri === data.length - 1, color: DARK })]
          })]
        }))
      }))
    ]
  });
}

function costBreakdownTable() {
  const colWidths = [5360, 2000, 2000];
  const headers = ["Component", "Hours", "Amount (USD)"];
  const rows = [
    ["Discovery & Requirements", "56", "$1,400"],
    ["Backend Development", "140", "$3,500"],
    ["Frontend Development", "120", "$3,000"],
    ["AI Service Development (OpenAI Integration Framework)", "48", "$1,200"],
    ["GPS & Payment Integration", "40", "$1,000"],
    ["Database Design & Setup", "28", "$700"],
    ["Authentication & Security", "24", "$600"],
    ["Reporting, Analytics & Accounting Module", "36", "$900"],
    ["Collection Automation", "20", "$500"],
    ["Multi-Country, Multi-Branch & Multi-Currency Setup", "28", "$700"],
    ["File Storage & Documents", "20", "$500"],
    ["Testing & QA", "32", "$800"],
    ["Deployment & DevOps", "20", "$500"],
    ["Documentation & Training", "28", "$700"],
    ["Project Management", "20", "$500"],
    ["Development Subtotal", "560", "$16,500"],
    ["Accelerated Delivery Premium (45-day timeline)", "", "$900"],
    ["Professional Discount", "", "-$2,900"],
    ["TOTAL INVESTMENT", "", "$14,500"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...rows.map((row, ri) => {
        const isTotal = row[0] === "TOTAL INVESTMENT";
        const isSubtotal = row[0].includes("Subtotal") || row[0].includes("Discount") || row[0].includes("Premium");
        const bg = isTotal ? LIGHT_BLUE : isSubtotal ? GRAY_BG : (ri % 2 === 0 ? WHITE : "F8F8F8");
        return new TableRow({
          children: row.map((cell, i) => new TableCell({
            borders,
            width: { size: colWidths[i], type: WidthType.DXA },
            shading: { fill: bg, type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            children: [new Paragraph({ alignment: i > 0 ? AlignmentType.CENTER : AlignmentType.LEFT, children: [new TextRun({ text: cell, font: "Arial", size: 18, bold: isTotal || isSubtotal, color: DARK })] })]
          }))
        });
      })
    ]
  });
}

function notIncludedTable() {
  const colWidths = [3360, 3000, 3000];
  const headers = ["Item", "Responsible Party", "Estimated Cost"];
  const rows = [
    ["Cloud Hosting (AWS/Azure/GCP)", "Client", "$150-300/month"],
    ["OpenAI API Usage Costs", "Client", "Variable (usage-based)"],
    ["Domain Name & SSL Certificate", "Client", "$20-100/year"],
    ["GPS Hardware Devices", "Client", "Per device"],
    ["Payment Gateway Merchant Fees", "Client", "2.5% + $0.30/txn"],
    ["SMS/Email Service Provider", "Client", "Per message"],
    ["WhatsApp Business API", "Client", "Variable"],
    ["Database Hosting (RDS)", "Client", "Included in hosting"],
    ["File Storage (AWS S3)", "Client", "Variable"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((cell, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: ri % 2 === 0 ? WHITE : GRAY_BG, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ alignment: i > 0 ? AlignmentType.CENTER : AlignmentType.LEFT, children: [new TextRun({ text: cell, font: "Arial", size: 18, color: DARK })] })]
        }))
      }))
    ]
  });
}

function timelineTable() {
  const colWidths = [2600, 1100, 5660];
  const headers = ["Phase", "Duration", "Deliverables"];
  const rows = [
    ["Phase 1: Discovery & Planning", "4 days", "Requirements, Architecture, Database design, Wireframes"],
    ["Phase 2: Backend Development", "12 days", "APIs, Authentication, Core modules, Database setup"],
    ["Phase 3: Frontend - Operations", "8 days", "All dashboards, Alerts, Tasks, Calendar"],
    ["Phase 4: Frontend - Fleet & Drivers", "7 days", "Vehicle management, Driver management"],
    ["Phase 5: AI Customer Service", "5 days", "Customer portal, AI chatbot integration"],
    ["Phase 6: Collection Automation", "3 days", "Reminder system, Multi-channel notifications"],
    ["Phase 7: Financial & Accounting Module", "4 days", "Payments, Invoices, Expenses, Accounting, Reports"],
    ["Phase 8: Multi-Country/Currency Setup", "3 days", "Multi-branch, multi-currency, multi-country configuration"],
    ["Phase 9: Integrations", "4 days", "GPS, Payment gateway, Email/SMS"],
    ["Phase 10: Testing & QA", "5 days", "Testing, Bug fixes, Performance optimization"],
    ["Phase 11: Deployment & Training", "3 days", "Production deployment, Training, Handover"],
    ["TOTAL", "45 Working Days", "Complete Fleet Management & AI ERP System"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...rows.map((row, ri) => {
        const isLast = ri === rows.length - 1;
        return new TableRow({
          children: row.map((cell, i) => new TableCell({
            borders,
            width: { size: colWidths[i], type: WidthType.DXA },
            shading: { fill: isLast ? LIGHT_BLUE : ri % 2 === 0 ? WHITE : GRAY_BG, type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [new TextRun({ text: cell, font: "Arial", size: 18, bold: isLast, color: DARK })] })]
          }))
      });
      })
    ]
  });
}

function riskTable() {
  const colWidths = [2200, 1200, 1200, 4760];
  const headers = ["Risk", "Probability", "Impact", "Mitigation Strategy"];
  const rows = [
    ["Client API Delays", "High", "High", "APIs must be ready before development; mock APIs used during development"],
    ["OpenAI Cost Overrun", "Medium", "Medium", "Client manages OpenAI API budget; ByteBoot not liable for AI usage costs"],
    ["Third-Party Service Changes", "Medium", "Medium", "Flexible integration framework; monitoring of service updates"],
    ["UAT Delays", "Medium", "High", "Daily UAT sessions; dedicated client resources required"],
    ["Scope Creep", "Medium", "High", "Formal change request process; clear scope documentation"],
    ["Infrastructure Issues", "Low", "High", "Comprehensive testing; backup procedures"],
    ["Regulatory Changes", "Low", "High", "Client responsible for compliance; software designed for flexibility"],
    ["Multi-Currency Sync Issues", "Low", "Medium", "Robust currency conversion engine; daily rate refresh testing"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 100, right: 100 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((cell, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: ri % 2 === 0 ? WHITE : GRAY_BG, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          children: [new Paragraph({ children: [new TextRun({ text: cell, font: "Arial", size: 18, color: DARK })] })]
        }))
      }))
    ]
  });
}

function amcTable() {
  const colWidths = [4680, 4680];
  const headers = ["Service Component", "Annual Cost"];
  const rows = [
    ["Software Maintenance & Support", "10-20% of project cost ($1,450-$2,900/year)"],
    ["Bug Fixes and Updates", "Included in AMC"],
    ["Security Patches", "Included in AMC"],
    ["Performance Monitoring", "Included in AMC"],
    ["Technical Support (Email/Phone)", "Included in AMC"],
    ["Minor Enhancements", "Up to 20 hours/year included"],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: BLUE, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, font: "Arial", size: 18, bold: true, color: WHITE })] })]
        }))
      }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((cell, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: ri % 2 === 0 ? WHITE : GRAY_BG, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: cell, font: "Arial", size: 18, color: DARK })] })]
        }))
      }))
    ]
  });
}

function signatureBlock(party, name, designation, date, signed) {
  const colWidths = [2400, 6960];
  const rows = [
    ["Name:", name],
    ["Designation:", designation],
    ["Date:", date],
    ["Signature:", signed ? signed : "________________________"],
    ["Company Stamp:", ""],
  ];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        children: [
          new TableCell({
            columnSpan: 2,
            borders,
            width: { size: 9360, type: WidthType.DXA },
            shading: { fill: BLUE, type: ShadingType.CLEAR },
            margins: { top: 100, bottom: 100, left: 200, right: 200 },
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: party, font: "Arial", size: 22, bold: true, color: WHITE })] })]
          })
        ]
      }),
      ...rows.map(([label, val]) => new TableRow({
        children: [
          new TableCell({
            borders,
            width: { size: 2400, type: WidthType.DXA },
            shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: label, font: "Arial", size: 20, bold: true, color: BLUE })] })]
          }),
          new TableCell({
            borders,
            width: { size: 6960, type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({ children: [new TextRun({ text: val, font: "Arial", size: 20, color: DARK })] })]
          })
        ]
      }))
    ]
  });
}

const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: "Arial", color: BLUE }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: "Arial", color: MID_BLUE }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: MID_BLUE, space: 4 } },
            spacing: { after: 80 },
            children: [
              new TextRun({ text: "SOFTWARE DEVELOPMENT AGREEMENT", font: "Arial", size: 18, bold: true, color: BLUE }),
              new TextRun({ text: "  |  Ola Cars Fleet Management & AI ERP System  |  ByteBoot Techno Solutions Pvt Ltd", font: "Arial", size: 16, color: "666666" })
            ]
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: MID_BLUE, space: 4 } },
            spacing: { before: 80 },
            tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
            children: [
              new TextRun({ text: "CONFIDENTIAL - Ola Cars Rental Services", font: "Arial", size: 16, color: "666666" }),
              new TextRun({ text: "\tPage ", font: "Arial", size: 16, color: "666666" }),
              new PageNumber(),
            ]
          })
        ]
      })
    },
    children: [
      // COVER PAGE
      spacer(4),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: "SOFTWARE DEVELOPMENT AGREEMENT", font: "Arial", size: 52, bold: true, color: BLUE })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: MID_BLUE, space: 6 } },
        spacing: { before: 0, after: 240 },
        children: [new TextRun({ text: "Fleet Management & AI ERP System", font: "Arial", size: 36, bold: true, color: MID_BLUE })]
      }),
      spacer(1),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "Between ByteBoot Techno Solutions Pvt Ltd and Ola Cars Rental Services", font: "Arial", size: 22, color: DARK })]
      }),
      spacer(3),
      headerTable([
        ["Document No:", "OLA-CUSTOM-SDA-04/2026"],
        ["Date:", "February 24, 2026"],
        ["Agreement Date:", "February 24, 2026"],
        ["Total Pages:", "Comprehensive Agreement"],
        ["Total Project Value:", "USD 14,500.00 (Fourteen Thousand Five Hundred US Dollars Only)"],
        ["Timeline:", "45 Working Days"],
        ["Project Start:", "Monday, February 24, 2026"],
        ["Project End:", "Wednesday, April 29, 2026"],
        ["Status:", "Pending Signature"],
      ]),
      spacer(3),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "PARTIES TO THIS AGREEMENT", font: "Arial", size: 20, bold: true, color: BLUE })] }),
      spacer(1),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4580, 4780],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4580, type: WidthType.DXA },
                shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
                margins: { top: 120, bottom: 120, left: 180, right: 180 },
                children: [
                  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "SERVICE PROVIDER", font: "Arial", size: 20, bold: true, color: BLUE })] }),
                  spacer(1),
                  para("ByteBoot Techno Solutions Pvt Ltd"),
                  para("B5, 1st Floor, Pais Avenue"),
                  para("Waterland Road, Elamkulam"),
                  para("Kochi, Kerala, India - 682020"),
                  para("Ph: 0484-3135340 | Mob: +91-8921227706"),
                  para("Email: contact@byteboot.in"),
                  para("Website: www.byteboot.in"),
                  para("ISO 9001-2015 Certified Company"),
                ]
              }),
              new TableCell({
                borders,
                width: { size: 4780, type: WidthType.DXA },
                shading: { fill: GRAY_BG, type: ShadingType.CLEAR },
                margins: { top: 120, bottom: 120, left: 180, right: 180 },
                children: [
                  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "CLIENT", font: "Arial", size: 20, bold: true, color: BLUE })] }),
                  spacer(1),
                  para("Ola Cars Rental Services"),
                  para("[Client Address Line 1]"),
                  para("[Client Address Line 2]"),
                  para("[City, Country]"),
                  para("[Phone Number]"),
                  para("[Email Address]"),
                  para("[Website if applicable]"),
                  para("[Registration/Company Number]"),
                ]
              })
            ]
          })
        ]
      }),

      pageBreak(),

      // SECTION 1
      h1("1. PROJECT OVERVIEW"),
      h2("1.1 Project Description"),
      para("ByteBoot Techno Solutions Pvt Ltd (hereinafter referred to as 'ByteBoot' or 'Service Provider') agrees to design, develop, and deliver a comprehensive, cloud-hosted, custom-built Fleet Management and AI-powered ERP System for Ola Cars Rental Services (hereinafter referred to as 'Client'). The system shall be built using modern web technologies including React.js, Node.js/Django, and Python AI services."),
      para("This agreement supersedes and replaces all prior proposals, quotations, or discussions, including any previously proposed Zoho platform configuration, and constitutes the complete and binding agreement between the parties."),
      spacer(1),
      h2("1.2 System Objectives"),
      bullet("Complete automation of fleet operations, customer service, and financial collection processes"),
      bullet("Real-time GPS integration for live vehicle monitoring and driver behavior tracking"),
      bullet("AI-powered customer service portal with 24/7 chatbot support using OpenAI GPT-4"),
      bullet("Automated payment collection reminder system with multi-channel delivery"),
      bullet("Workshop management, maintenance alerts, and driver monitoring"),
      bullet("Multi-country, multi-branch, and multi-currency operational support"),
      bullet("Integrated accounting and financial management with consolidated reporting"),
      bullet("Complete code ownership with no subscription fees or vendor lock-in"),
      spacer(1),
      h2("1.3 Document References"),
      para("This agreement is based on and incorporates the following reference documents:"),
      bullet("Proposal Document No: OLA-CUSTOM-03/2026, Dated: February 14, 2026"),
      bullet("Payment Terms & Milestone Schedule, Dated: February 20, 2026"),
      bullet("Revised Technical Scope and Feature Specifications as annexed hereto"),

      pageBreak(),

      // SECTION 2
      h1("2. SCOPE OF WORK"),
      h2("2.1 Technical Specifications"),
      h3("Frontend Technology Stack"),
      bullet("Framework: React.js with Material-UI / Ant Design"),
      bullet("State Management: Redux / Zustand"),
      bullet("Analytics & Reporting: Recharts / D3.js"),
      bullet("Languages: HTML5, CSS3, JavaScript/TypeScript"),
      bullet("Responsive Design: Mobile-first, WCAG 2.1 compliant"),
      spacer(1),
      h3("Backend Technology Stack"),
      bullet("Primary Server: Node.js with Express.js OR Django + REST Framework"),
      bullet("Database: PostgreSQL (robust relational database)"),
      bullet("Cache: Redis for session management and performance"),
      bullet("API Architecture: RESTful APIs with JWT authentication"),
      bullet("Real-time: WebSocket for live notifications"),
      spacer(1),
      h3("AI Service Layer"),
      bullet("Platform: Python + FastAPI"),
      bullet("AI Engine: OpenAI GPT-4 (via integration framework - API costs are Client's responsibility)"),
      bullet("Conversation Management: LangChain"),
      bullet("Natural Language Processing for customer queries"),
      spacer(1),
      h3("Security & Compliance"),
      bullet("SSL/TLS encryption for all data transmission"),
      bullet("AES-256 encryption for sensitive data storage"),
      bullet("Role-based access control (RBAC) with granular permissions"),
      bullet("SQL injection, XSS, and CSRF protection"),
      bullet("Rate limiting and audit trail logging"),
      spacer(1),
      h2("2.2 System Modules"),
      h3("2.2.1 Operations Management"),
      para("Four primary dashboards: Executive Dashboard (fleet overview, revenue metrics, KPIs), Collections Dashboard (outstanding payments, aging analysis), Workshop Dashboard (maintenance queue, work orders), and GPS & Risk Dashboard (real-time tracking, driver behavior). Includes an Alert Center for payment overdue, maintenance due, GPS violations, and document expiry reminders."),
      spacer(1),
      h3("2.2.2 Fleet Management"),
      para("Complete vehicle registration, inventory, and lifecycle management. Operational status tracking (available, rented, maintenance, retired). Document management, vehicle timeline, importation records, assignment management, insurance and claims tracking, incident reports, and detailed cost/profitability analysis per vehicle."),
      spacer(1),
      h3("2.2.3 Drivers Module"),
      para("Driver onboarding with document verification and license verification workflow. Active driver management with performance metrics, GPS behavior scores, status management, and contract creation and renewal workflows."),
      spacer(1),
      h3("2.2.4 AI-Powered Customer Service Portal"),
      para("Secure customer login with personalized dashboard. The AI chatbot (powered by OpenAI GPT-4) provides 24/7 automated support, natural language query understanding, real-time data retrieval (vehicle availability, payment status, rental details), smart escalation to human agents, and full conversation history. Supported query types include vehicle availability, rental status, payment information, GPS tracking, and roadside assistance."),
      para("IMPORTANT: The OpenAI API usage cost is entirely the Client's responsibility. ByteBoot will build and integrate the framework; however, all API call fees, token costs, and associated OpenAI charges are billed directly to the Client's OpenAI account. ByteBoot has no liability for these ongoing operational costs."),
      spacer(1),
      h3("2.2.5 Automated Collection System"),
      para("Pre-payment reminder sequence: 7 days before (Email + SMS), 3 days before (reminder with payment link), 1 day before (final reminder), and due date notification. Overdue management escalation matrix from daily reminders (Days 1-3) to manager escalation (Day 4) to weekly reminders with late fees (Days 8-14) to vehicle recovery alert and legal notice generation (Day 15). Multi-channel delivery: Email, SMS, WhatsApp (optional), and in-app notifications."),
      spacer(1),
      h3("2.2.6 Financial Management"),
      para("Payment collection recording (cash, card, bank transfer), payment status tracking and history. Auto-generated invoices with customizable templates, PDF download, and email delivery. Expense tracking with categories, receipt upload, and vehicle-specific cost allocation."),
      spacer(1),
      h3("2.2.7 Accounting & Financial Reporting Module"),
      para("A comprehensive double-entry accounting system integrated into the platform:"),
      bullet("General Ledger: Chart of accounts setup, journal entry posting (manual and automated), account balance tracking, trial balance generation, and period-end closing procedures"),
      bullet("Loan & Rental Accounting: Disbursement entries, collection accounting, interest/income recognition, fee recording, provisions, and write-off accounting"),
      bullet("Financial Statements: Balance sheet, Profit & Loss statement, cash flow statement, aging analysis, and portfolio quality reports"),
      bullet("Bank Reconciliation: Bank statement import, transaction matching, reconciliation interface, and outstanding items management"),
      bullet("Tax Compliance: Tax calculation and recording, tax payment tracking, and applicable VAT/GST report generation"),
      bullet("Accounts Receivable & Payable: Full AR/AP module with aging buckets, collection performance, and vendor management"),
      bullet("Report Builder: Custom report builder with parameter-based filtering, drill-down, export to PDF/Excel/CSV, and scheduled report generation"),
      bullet("Audit Trail: Comprehensive logging of all financial transactions with user attribution"),
      spacer(1),
      h3("2.2.8 GPS & Maintenance"),
      para("Real-time GPS tracking with live vehicle location, movement status, mileage tracking, and geofence alerts. Risk monitoring for speed violations, harsh braking/acceleration, after-hours usage, and driver behavior scoring. Automated maintenance alerts (mileage-based and time-based). Workshop operations: work order creation, technician assignment, parts inventory, and service billing."),
      spacer(1),
      h2("2.3 Multi-Country, Multi-Branch & Multi-Currency Support"),
      para("The system shall be designed and built to support Ola Cars' multi-geography and multi-entity operations:"),
      h3("2.3.1 Multi-Country Support"),
      bullet("Country-specific configuration profiles (tax rates, regulations, date/number formats)"),
      bullet("Country-level reporting and analytics with consolidated roll-up views"),
      bullet("Localized document templates per country"),
      bullet("Country-specific compliance fields and workflows"),
      bullet("Ability to add new countries through system administration (no code changes required)"),
      spacer(1),
      h3("2.3.2 Multi-Branch Support"),
      bullet("Hierarchical organization structure: Company > Country > Branch"),
      bullet("Branch-level vehicle inventory, driver pools, and staff management"),
      bullet("Cross-branch vehicle transfer and assignment capabilities"),
      bullet("Branch-level financial tracking with consolidated company-wide reporting"),
      bullet("Branch managers can view and manage only their branch; admins have full visibility"),
      bullet("Inter-branch reconciliation and transfer accounting entries"),
      spacer(1),
      h3("2.3.3 Multi-Currency Support"),
      bullet("Configurable base currency per country/branch"),
      bullet("Real-time currency exchange rate integration (via external API - Client's account)"),
      bullet("Automatic currency conversion for cross-branch transactions and reporting"),
      bullet("Consolidated financial reporting in a single base currency with subsidiary breakdowns"),
      bullet("Multi-currency invoice generation and payment recording"),
      bullet("Currency gain/loss accounting entries"),
      bullet("Historical exchange rate storage for audit and reporting purposes"),

      pageBreak(),

      // SECTION 3 - SYSTEM WORKFLOWS
      h1("3. SYSTEM WORKFLOWS"),
      h2("3.1 Customer Service Workflow"),
      numbered("Customer logs in to self-service portal with secure credentials"),
      numbered("AI chatbot handles queries: availability, payment, rental status"),
      numbered("System retrieves real-time data from backend for accurate responses"),
      numbered("Complex queries escalated to human agents with full context"),
      numbered("Conversation history stored for quality assurance and training"),
      spacer(1),
      h2("3.2 Collection Workflow"),
      numbered("System identifies upcoming due dates and triggers pre-due reminder sequence"),
      numbered("Customer makes payment via payment link or gateway"),
      numbered("Payment confirmation and digital receipt generated automatically"),
      numbered("If payment missed: escalation matrix activates (Days 1-3 reminders, Day 4 manager alert)"),
      numbered("Continued non-payment triggers vehicle recovery alert and legal notice generation"),
      numbered("Overdue amounts auto-updated in collections dashboard with aging bucket classification"),
      spacer(1),
      h2("3.3 Multi-Branch Financial Workflow"),
      numbered("Transactions recorded at branch level with branch code attribution"),
      numbered("Branch-level reports available to branch managers in real time"),
      numbered("Automatic consolidation engine rolls up data to country level"),
      numbered("Country-level data consolidated to company-wide dashboard for admin/executive"),
      numbered("Currency conversion applied at consolidation level using configured exchange rates"),
      numbered("Inter-branch transfers generate matching accounting entries in both branches"),

      pageBreak(),

      // SECTION 4 - INTEGRATION REQUIREMENTS
      h1("4. INTEGRATION REQUIREMENTS"),
      h2("4.1 Third-Party API Integration Framework"),
      para("ByteBoot will develop the integration framework and API connectivity layer for the following services. All API accounts, credentials, ongoing subscription costs, and associated third-party charges are the Client's sole responsibility."),
      spacer(1),
      h3("GPS & Tracking"),
      bullet("Real-time GPS API (Client to provide provider and credentials)"),
      bullet("Mileage synchronization, driver behavior monitoring, geofence alert generation"),
      spacer(1),
      h3("Payment Gateway"),
      bullet("Stripe / Razorpay / PayPal integration framework"),
      bullet("Payment link generation, webhook handling, and transaction logging"),
      bullet("Client is responsible for merchant account setup and transaction fees"),
      spacer(1),
      h3("Communication Services"),
      bullet("Email: SendGrid / AWS SES integration"),
      bullet("SMS: Twilio / Lab Mobiles / AWS SNS integration"),
      bullet("WhatsApp Business API (optional - Client's account and costs)"),
      bullet("In-app real-time notifications via WebSocket"),
      spacer(1),
      h3("AI Service (OpenAI)"),
      bullet("OpenAI GPT-4 API integration framework for chatbot and intelligent query handling"),
      bullet("LangChain conversation management framework"),
      bullet("IMPORTANT: All OpenAI API usage fees are the Client's direct responsibility. ByteBoot builds the integration; the Client must provide their own OpenAI API key and manage their OpenAI account and billing. ByteBoot is not liable for any AI token usage costs, rate limits, or OpenAI policy changes."),
      spacer(1),
      h3("Currency Exchange Rates"),
      bullet("Open exchange rates API or equivalent (Client to select and provide credentials)"),
      bullet("Automated daily rate refresh for multi-currency operations"),
      spacer(1),
      h3("File Storage"),
      bullet("AWS S3 / Google Cloud Storage (Client-provided account)"),
      bullet("Document upload/download and CDN integration"),
      spacer(1),
      h2("4.2 Client Infrastructure Requirements"),
      para("Client must provide and maintain prior to project commencement:"),
      bullet("Cloud hosting account (AWS, Google Cloud, or Azure) with admin credentials"),
      bullet("Production and staging server environments"),
      bullet("Domain name registration and SSL certificate"),
      bullet("OpenAI API account and API key (for AI chatbot functionality)"),
      bullet("GPS service provider account and API credentials"),
      bullet("Payment gateway merchant account and API keys"),
      bullet("SMS/Email service provider accounts and API keys"),
      bullet("Currency exchange rate API account (for multi-currency)"),
      bullet("File storage service (AWS S3 or equivalent)"),

      pageBreak(),

      // SECTION 5 - TIMELINE
      h1("5. TIMELINE & DELIVERABLES"),
      h2("5.1 Project Schedule"),
      headerTable([
        ["Project Start Date:", "Monday, February 24, 2026"],
        ["Project End Date:", "Wednesday, April 29, 2026"],
        ["Total Working Days:", "45 (excluding weekends and public holidays)"],
        ["Total Calendar Days:", "Approximately 66 days"],
        ["Holidays Excluded:", "March 20 (Eid-ul-Fitr), April 3 (Good Friday), April 15 (Vishu), All Saturdays & Sundays"],
      ]),
      spacer(1),
      h2("5.2 Development Phases"),
      timelineTable(),
      spacer(1),
      h2("5.3 Project Deliverables"),
      h3("Software Products"),
      bullet("Complete React.js frontend application (responsive, mobile-first)"),
      bullet("Complete Node.js/Django backend with RESTful APIs"),
      bullet("Python AI service layer with OpenAI integration framework"),
      bullet("Multi-country, multi-branch, multi-currency configuration engine"),
      bullet("Integrated accounting and financial reporting module"),
      bullet("Automated collection and notification system"),
      bullet("Complete database schema and migrations"),
      bullet("Full source code repository access via GitHub/GitLab"),
      spacer(1),
      h3("Documentation"),
      bullet("User Manual for Customer Portal"),
      bullet("Admin Dashboard User Manual with screenshots"),
      bullet("Technical API Documentation (Swagger)"),
      bullet("Database Schema Documentation (ERD diagrams)"),
      bullet("Deployment and Configuration Guide"),
      bullet("System Architecture Document"),
      bullet("Multi-Branch & Multi-Currency Configuration Guide"),
      bullet("Accounting Module User Guide"),
      bullet("Training Materials"),
      spacer(1),
      h3("Support & Training"),
      bullet("60 days free post-launch support (bug fixes, security patches, minor adjustments)"),
      bullet("3 remote training sessions (2 hours each) via video conference"),
      bullet("Knowledge transfer sessions"),

      pageBreak(),

      // SECTION 6 - FINANCIAL TERMS
      h1("6. FINANCIAL TERMS"),
      h2("6.1 Development Cost Breakdown"),
      costBreakdownTable(),
      spacer(1),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120 },
        children: [new TextRun({ text: "Agreed Project Cost: USD 14,500.00 (Fourteen Thousand Five Hundred US Dollars Only)", font: "Arial", size: 22, bold: true, color: BLUE })]
      }),
      spacer(1),
      h2("6.2 Payment & Milestone Schedule"),
      milestoneTable(),
      spacer(1),
      h2("6.3 Payment Terms & Conditions"),
      h3("Milestone 1 Payment (30% - $4,350.00)"),
      bullet("Due upon signing of this agreement"),
      bullet("Project commencement contingent upon receipt of this payment"),
      bullet("Covers project planning, architecture design, and environment setup"),
      spacer(1),
      h3("Milestone 2 Payment (20% - $2,900.00)"),
      bullet("Due upon completion of Phase 1: backend APIs, database, authentication"),
      bullet("All core APIs must be functional and demonstrable in staging environment"),
      spacer(1),
      h3("Milestone 3 Payment (20% - $2,900.00)"),
      bullet("Due upon completion of Phase 2: operations dashboards, fleet & driver management UI"),
      bullet("All dashboards and management interfaces functional in staging environment"),
      spacer(1),
      h3("Milestone 4 Payment (20% - $2,900.00)"),
      bullet("Due upon completion of Phase 3: AI customer service, collection automation, integrations"),
      bullet("AI chatbot operational (requires Client's OpenAI API key), collection automation functional"),
      spacer(1),
      h3("Milestone 5 Payment (10% - $1,450.00)"),
      bullet("Due upon final delivery: testing complete, production deployment, training completed"),
      bullet("All critical and major issues resolved, client sign-off obtained"),
      bullet("No deployment to production until final payment received"),
      spacer(1),
      h2("6.4 What IS Included in the Development Cost ($14,500)"),
      bullet("Complete custom web application development (frontend + backend + AI service layer)"),
      bullet("All system modules as specified in Section 2"),
      bullet("Multi-country, multi-branch, and multi-currency configuration engine"),
      bullet("Integrated double-entry accounting and financial reporting module"),
      bullet("OpenAI GPT-4 integration framework (API usage costs are Client's responsibility)"),
      bullet("Database design, implementation, and optimization"),
      bullet("Security implementation and testing"),
      bullet("Comprehensive QA, bug fixes during development and UAT"),
      bullet("Complete documentation set as listed in Section 5.3"),
      bullet("3 remote training sessions and 60 days free post-launch support"),
      bullet("Production deployment assistance"),
      spacer(1),
      h2("6.5 What is NOT Included (Client's Responsibility)"),
      para("The following costs are NOT included in the $14,500 development fee and must be arranged and funded separately by the Client:"),
      notIncludedTable(),
      spacer(1),
      para("Note: ByteBoot has no control over and bears no liability for any third-party service costs, including OpenAI API usage fees which are entirely usage-dependent and billed directly to the Client's accounts."),
      spacer(1),
      h2("6.6 Late Payment"),
      bullet("Payments must be made within 5 business days of milestone completion and Client approval"),
      bullet("Late payment may result in suspension of development work"),
      bullet("No deployment or training until final payment received"),
      bullet("ByteBoot reserves the right to withhold source code delivery until all outstanding payments are cleared"),

      pageBreak(),

      // SECTION 7 - TERMS AND CONDITIONS
      h1("7. TERMS AND CONDITIONS"),
      h2("7.1 Project Commencement"),
      bullet("Project work shall commence within 3 business days of receiving Milestone 1 payment ($4,350) and signed agreement"),
      bullet("Client must provide all required credentials, API keys, and infrastructure access within 5 business days of project commencement"),
      bullet("Delays in providing required materials or API access may impact the agreed 45-day timeline"),
      spacer(1),
      h2("7.2 Change Requests"),
      bullet("Changes to agreed specifications must be submitted in writing via formal change request"),
      bullet("Minor UI/UX adjustments within same functionality: No additional charge"),
      bullet("Additional features or modules beyond specified scope: Chargeable at $50/hour"),
      bullet("Major functionality changes: Subject to additional fees and timeline extension"),
      bullet("Change requests during UAT phase may impact final deployment date"),
      spacer(1),
      h2("7.3 Client Responsibilities"),
      h3("7.3.1 Data and Content Provision (within 5 business days of commencement)"),
      bullet("Company logos, branding materials, and brand guidelines"),
      bullet("Business process workflows and operational policies"),
      bullet("Fleet categories, pricing structures, and rental terms"),
      bullet("Accounting chart of accounts structure"),
      bullet("Multi-branch organizational hierarchy and country configurations"),
      bullet("Currency configuration requirements and preferred exchange rate provider"),
      bullet("Report templates and requirements"),
      bullet("Legal documents content (Terms of Service, Privacy Policy, rental agreements)"),
      spacer(1),
      h3("7.3.2 API Access and Credentials (CRITICAL - Must Be Ready)"),
      bullet("OpenAI API account, API key, and sufficient credit balance"),
      bullet("GPS service provider account and API credentials"),
      bullet("Payment gateway merchant account and API keys"),
      bullet("SMS/Email service provider accounts and API keys"),
      bullet("Cloud hosting account with admin credentials"),
      bullet("Currency exchange rate API credentials"),
      para("CRITICAL: Delays in providing any API access will directly delay project completion. Some third-party API approvals may take 2-4 weeks. Client should initiate these immediately."),
      spacer(1),
      h3("7.3.3 Timely Feedback and Approvals"),
      bullet("Respond to design mockups and demonstrations within 3 business days"),
      bullet("Complete User Acceptance Testing within the agreed 10-day UAT period"),
      bullet("Designate a single point of contact with decision-making authority"),
      bullet("Provide consolidated feedback (not fragmented feedback from multiple stakeholders simultaneously)"),
      spacer(1),
      h2("7.4 Intellectual Property & Usage Rights"),
      h3("7.4.1 Ownership"),
      bullet("Client will own all rights to the custom-developed application upon full payment completion"),
      bullet("Source code ownership transfers to Client after final payment (Milestone 5: $1,450)"),
      bullet("Client receives complete source code repository access via GitHub/GitLab"),
      bullet("Database schema and all custom code become Client property"),
      spacer(1),
      h3("7.4.2 Usage Rights"),
      bullet("Exclusive Business Use: Platform developed exclusively for Ola Cars Rental Services operations"),
      bullet("Multi-Country & Multi-Branch Use: Client may deploy across all its own branches and countries"),
      bullet("Commercial Operations: Client may operate the platform commercially for its rental business"),
      bullet("Internal Modifications: Client may modify code for internal business use after delivery"),
      bullet("Cannot resell the platform as a SaaS offering or white-label it to competitors"),
      bullet("Cannot distribute source code to third parties without ByteBoot's written acknowledgment"),
      spacer(1),
      h3("7.4.3 ByteBoot Rights"),
      bullet("ByteBoot retains rights to general methodologies, frameworks, and non-client-specific reusable components"),
      bullet("ByteBoot may showcase project in portfolio with Client permission (business name may be anonymized)"),
      bullet("ByteBoot cannot use Client-specific business logic, branding, or proprietary data in other projects"),
      spacer(1),
      h2("7.5 Data Security & Confidentiality"),
      h3("7.5.1 ByteBoot Commitments"),
      bullet("Maintain strict confidentiality of all Client data, business information, and proprietary processes"),
      bullet("Implement industry-standard security measures during development (HTTPS, AES-256, JWT)"),
      bullet("Restrict access to authorized development team members only"),
      bullet("Sign individual non-disclosure agreements with all team members"),
      bullet("Securely delete Client-specific data from development systems after project completion"),
      spacer(1),
      h3("7.5.2 Mutual Confidentiality"),
      bullet("Both parties agree to maintain confidentiality of proprietary information shared during the project"),
      bullet("Confidentiality obligations survive termination of this agreement indefinitely"),
      bullet("Neither party shall disclose terms of this agreement without written consent"),
      spacer(1),
      h2("7.6 Support & Maintenance"),
      h3("7.6.1 Free Support Period (60 Days Post-Launch)"),
      para("Included: Bug fixes, performance optimization, security patches, minor UI adjustments, email and phone technical support during business hours (Mon-Fri, 9 AM - 6 PM IST)."),
      para("Response Times: Critical issues (system down) within 4 hours; Major issues within 24 hours; Minor issues within 72 hours."),
      para("Excluded: New feature development, major design overhauls, additional third-party integrations beyond original scope, issues caused by Client modifications, issues caused by third-party service failures (including OpenAI outages), infrastructure management."),
      spacer(1),
      h3("7.6.2 Support Contacts"),
      bullet("Project Manager: Anas K S | anaz.k@byteboot.in | +91-9778527748"),
      bullet("Project Coordinator: Anjali M S | anjali@byteboot.in | +91-8075119654"),
      bullet("General Support: contact@byteboot.in"),
      spacer(1),
      h3("7.6.3 Post Free-Support Period Maintenance (Optional AMC)"),
      amcTable(),
      spacer(1),
      h3("7.6.4 Additional Chargeable Services"),
      bullet("Additional training sessions: $50/hour"),
      bullet("Custom development work: $50/hour"),
      bullet("Emergency support (outside business hours): $75/hour"),
      bullet("On-site support (outside India): Daily rate + travel expenses"),
      spacer(1),
      h2("7.7 Hosting & Infrastructure"),
      bullet("Client is responsible for procuring and managing all cloud infrastructure"),
      bullet("Estimated monthly hosting cost: $150-300/month (varies by usage and scale)"),
      bullet("ByteBoot will provide infrastructure architecture recommendations and deployment assistance"),
      bullet("Application designed for horizontal scalability; Client responsible for scaling costs"),
      bullet("Daily automated backup scripts provided; Client responsible for backup storage costs"),
      bullet("Recovery Time Objective (RTO): Within 24 hours; Recovery Point Objective (RPO): Previous day's backup"),
      spacer(1),
      h2("7.8 Testing & Acceptance"),
      h3("7.8.1 Testing Phases"),
      bullet("Development Testing (Continuous): Unit testing, integration testing, API testing, security testing"),
      bullet("Internal QA (Week 5): Comprehensive ByteBoot QA, end-to-end workflow testing, bug fixing"),
      bullet("UAT (10 Days): Client testing with real-world scenarios, business process validation, sign-off"),
      spacer(1),
      h3("7.8.2 Issue Classification"),
      bullet("Critical (must fix before deployment): System unusable, data loss, security vulnerabilities, payment failures"),
      bullet("Major (should fix before deployment): Significant feature not working, incorrect calculations, workflow blockages"),
      bullet("Minor (can fix post-deployment): Cosmetic issues, non-critical validation errors"),
      bullet("Enhancement (future scope, not included in current cost): Nice-to-have features beyond agreed scope"),
      spacer(1),
      h3("7.8.3 Acceptance Timeline"),
      bullet("UAT period: 10 days following handover for testing"),
      bullet("Client must provide written acceptance or issue list within 7 days of UAT completion"),
      bullet("If no response within 7 days, system deemed accepted (unless critical issues exist)"),
      bullet("Final payment due upon written acceptance; deployment proceeds only after final payment"),

      pageBreak(),

      // SECTION 8 - WARRANTIES
      h1("8. WARRANTIES & LIMITATIONS"),
      h2("8.1 ByteBoot Warranties"),
      para("ByteBoot warrants that the software will be developed using industry-standard practices; the system will perform substantially as specified in this agreement; code will be free of malicious code, viruses, or backdoors; all deliverables will be original work or properly licensed third-party components; and the source code will be clean, documented, and maintainable."),
      para("Warranty Period: 60 days from final deployment (covered under free support period)."),
      spacer(1),
      h2("8.2 Limitations of Liability"),
      bullet("ByteBoot's maximum total liability is limited to the total project cost paid ($14,500)"),
      bullet("ByteBoot is NOT liable for: indirect, consequential, or special damages; business losses; data loss from Client infrastructure failures; third-party service failures including OpenAI outages, GPS service failures, payment gateway failures; issues arising from Client modifications to delivered source code; regulatory fines or compliance issues"),
      spacer(1),
      h2("8.3 No Warranty for Third-Party Services & OpenAI"),
      bullet("ByteBoot provides the OpenAI integration framework only; the quality, availability, pricing, and performance of OpenAI services are entirely outside ByteBoot's control"),
      bullet("Client acknowledges that OpenAI may change its API, pricing, terms, or availability at any time; ByteBoot is not liable for any such changes or their impact on the system"),
      bullet("All other third-party integrations (GPS, payment gateway, SMS, currency API) are subject to their respective service terms"),
      spacer(1),
      h2("8.4 Client Acknowledgment"),
      para("Client acknowledges that software is provided based on agreed specifications; ByteBoot cannot guarantee specific business outcomes or ROI; actual system performance may vary based on infrastructure and usage patterns; Client is responsible for compliance with all applicable laws and regulations in all operating countries."),

      pageBreak(),

      // SECTION 9 - RISK
      h1("9. RISK FACTORS & MITIGATION"),
      riskTable(),

      pageBreak(),

      // SECTION 10 - TERMINATION
      h1("10. TERMINATION"),
      h2("10.1 Termination by Either Party"),
      bullet("Either party may terminate this agreement with 30 days written notice"),
      bullet("Client must pay for all work completed up to termination date"),
      bullet("ByteBoot will deliver all completed components upon receipt of payment for completed work"),
      spacer(1),
      h2("10.2 Termination for Cause (Material Breach)"),
      bullet("Non-payment beyond 30 days (by Client) constitutes material breach"),
      bullet("Failure to deliver agreed work (by ByteBoot) constitutes material breach"),
      bullet("Material breach by Client: ByteBoot retains all payments received"),
      bullet("Material breach by ByteBoot: Refund of payments for undelivered work"),
      bullet("15-day cure period provided for non-material breaches"),
      spacer(1),
      h2("10.3 Termination by Client (Convenience)"),
      bullet("Minimum payment: Milestone 1 payment ($4,350) is non-refundable"),
      bullet("Client pays for all completed work based on milestone completion percentage"),
      bullet("Client receives completed source code modules upon payment for completed portions"),

      pageBreak(),

      // SECTION 11 - DISPUTE RESOLUTION
      h1("11. DISPUTE RESOLUTION & GOVERNING LAW"),
      h2("11.1 Good Faith Negotiations"),
      para("All disputes shall first be attempted to resolve through good faith negotiations between senior management of both parties. Negotiation period: 30 days from written notice of dispute."),
      spacer(1),
      h2("11.2 Mediation"),
      para("If negotiation fails, disputes shall be submitted to mediation before a neutral third-party mediator. Mediation period: 30 days. Each party bears own mediation costs. Proceedings are confidential."),
      spacer(1),
      h2("11.3 Arbitration"),
      para("If mediation fails, disputes shall be resolved through binding arbitration. Arbitration decision is final and binding. Language: English."),
      spacer(1),
      h2("11.4 Governing Law"),
      para("This agreement shall be governed by and construed in accordance with the laws of Kerala, India. Any legal proceedings shall be subject to the exclusive jurisdiction of courts in Ernakulam, Kerala, India."),

      pageBreak(),

      // SECTION 12 - PROJECT TEAM
      h1("12. PROJECT TEAM & COMMUNICATION"),
      h2("12.1 ByteBoot Project Team"),
      bullet("Senior Full-Stack Developers: 3 (React.js, Node.js/Python)"),
      bullet("Backend Developers: 2 (API development, database optimization)"),
      bullet("Frontend Developers: 2 (UI/UX implementation, responsive design)"),
      bullet("DevOps Engineer: 1 (deployment, infrastructure)"),
      bullet("QA Engineer: 1 (testing and quality assurance)"),
      bullet("Project Manager: 1 (Anas K S - overall coordination)"),
      bullet("UI/UX Designer: 0.5 (design phase)"),
      para("Total Team: 10-11 members working in parallel for accelerated 45-day delivery."),
      spacer(1),
      h2("12.2 Communication Schedule"),
      bullet("Weekly Progress Review: 30-45 minutes (Client & ByteBoot PMs every Friday)"),
      bullet("Bi-Weekly Demo Sessions: 1 hour demonstrating completed modules"),
      bullet("Daily standups: Internal ByteBoot team coordination"),
      bullet("Ad-hoc meetings as needed for critical decisions or clarifications"),
      spacer(1),
      h2("12.3 Primary Contacts"),
      headerTable([
        ["ByteBoot Project Manager:", "Anas K S | anaz.k@byteboot.in | +91-9778527748"],
        ["ByteBoot Technical Lead:", "Pramod Gopinath | pramod.g@byteboot.in | +91-9141109785"],
        ["ByteBoot Coordinator:", "Anjali M S | anjali@byteboot.in | +91-8075119654"],
        ["Client Project Manager:", "________________________"],
        ["Client Technical Contact:", "________________________"],
        ["Client Business Contact:", "________________________"],
      ]),

      pageBreak(),

      // SECTION 13 - GENERAL PROVISIONS
      h1("13. GENERAL PROVISIONS"),
      h2("13.1 Force Majeure"),
      para("Neither party shall be liable for delays resulting from: natural disasters, war, pandemic, internet backbone failures, cyberattacks on critical infrastructure, power outages, or acts of God. Affected party must notify within 5 business days. If force majeure continues beyond 60 days, either party may terminate without penalty."),
      spacer(1),
      h2("13.2 Entire Agreement"),
      para("This agreement constitutes the entire agreement between parties, superseding all prior negotiations, representations, or understandings. Amendments must be in writing and signed by authorized representatives."),
      spacer(1),
      h2("13.3 Severability"),
      para("If any provision is found invalid or unenforceable, the remaining provisions remain in full force and effect."),
      spacer(1),
      h2("13.4 Assignment"),
      para("Neither party may assign this agreement without prior written consent, except in case of merger, acquisition, or sale of business. ByteBoot may subcontract specific technical tasks with Client notification."),
      spacer(1),
      h2("13.5 Independent Contractors"),
      para("ByteBoot is an independent contractor. Nothing in this agreement creates a partnership, joint venture, or employer-employee relationship. Each party is responsible for their own taxes and statutory obligations."),
      spacer(1),
      h2("13.6 Notices"),
      bullet("Client (Ola Cars): [Client Email Address] | [Client Address]"),
      bullet("ByteBoot: contact@byteboot.in | Room 104, DD Milestone, SA Road, Kadavanthra, Kerala, India"),
      para("All notices shall be in writing and delivered via email (with read receipt), registered mail, or courier with tracking."),

      pageBreak(),

      // SECTION 14 - SIGNATURES
      h1("14. ACCEPTANCE & SIGNATURES"),
      para("By signing below, both parties acknowledge that they have read, understood, and agree to be bound by all terms and conditions of this Software Development Agreement for the Ola Cars Fleet Management & AI ERP System."),
      spacer(2),
      signatureBlock("CLIENT: Ola Cars Rental Services", "________________________________", "________________________________", "________________________________", ""),
      spacer(2),
      signatureBlock("SERVICE PROVIDER: ByteBoot Techno Solutions Pvt Ltd", "Anusha V A", "Project Director", "February 24, 2026", ""),
      spacer(2),
      para("Document Version: 1.0  |  Last Updated: February 24, 2026  |  Document No: OLA-CUSTOM-SDA-04/2026"),
      para("Validity: This agreement is valid for 30 days from the date of issue."),
      spacer(1),
      para("This agreement is confidential and intended solely for Ola Cars Rental Services and ByteBoot Techno Solutions Pvt Ltd.", { center: true, color: "888888" }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/OlaCars_Software_Development_Agreement.docx", buffer);
  console.log("Document created successfully");
}).catch(err => {
  console.error("Error:", err);
  process.exit(1);
});