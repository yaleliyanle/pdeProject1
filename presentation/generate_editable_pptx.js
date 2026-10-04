const pptxgen = require("pptxgenjs");
const path = require("path");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Numerical PDE Coursework";
pptx.subject = "Numerical simulation of financial stochastic differential equations";
pptx.title = "Numerical Simulation of Financial Stochastic Differential Equations";
pptx.company = "Numerical Partial Differential Equations";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US"
};
pptx.defineSlideMaster({
  title: "COURSE",
  background: { color: "FFFFFF" },
  objects: [
    { rect: { x: 0, y: 0, w: 13.333, h: 0.56, fill: { color: "17365D" }, line: { color: "17365D" } } },
    { line: { x: 0, y: 7.18, w: 13.333, h: 0, line: { color: "168C8C", pt: 2 } } },
    { text: { text: "Numerical PDE Coursework", options: { x: 0.25, y: 7.20, w: 4.4, h: 0.2, fontFace: "Aptos", fontSize: 8, color: "667788", margin: 0 } } },
    { text: { text: "Financial SDE Numerical Methods", options: { x: 4.75, y: 7.20, w: 3.9, h: 0.2, fontFace: "Aptos", fontSize: 8, color: "168C8C", align: "center", margin: 0 } } },
    { text: { text: "September 2026", options: { x: 9.0, y: 7.20, w: 2.4, h: 0.2, fontFace: "Aptos", fontSize: 8, color: "667788", align: "right", margin: 0 } } }
  ],
  slideNumber: { x: 11.65, y: 7.19, w: 1.2, h: 0.22, color: "667788", fontFace: "Aptos", fontSize: 8, align: "right" }
});

const C = {
  navy: "17365D",
  teal: "168C8C",
  orange: "D97706",
  light: "EEF4F8",
  red: "B42318",
  text: "17212B",
  muted: "556575",
  white: "FFFFFF",
  line: "B8C7D1",
  paleRed: "FCEBE8",
  paleOrange: "FFF4E5"
};
const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const IC = path.join(ROOT, "individual_challenge");
const OUT = path.join(__dirname, "Financial_SDE_Numerical_Methods_Presentation_Editable.pptx");

function addTitle(slide, title) {
  slide.addText(title, {
    x: 0.35, y: 0.08, w: 12.6, h: 0.36,
    fontFace: "Aptos Display", fontSize: 24, bold: true,
    color: C.white, margin: 0, breakLine: false, fit: "shrink"
  });
}

function baseSlide(title) {
  const slide = pptx.addSlide("COURSE");
  addTitle(slide, title);
  return slide;
}

function addBodyText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: opts.fontFace || "Aptos",
    fontSize: opts.fontSize || 17,
    color: opts.color || C.text,
    bold: opts.bold || false,
    italic: opts.italic || false,
    align: opts.align || "left",
    valign: opts.valign || "top",
    margin: opts.margin === undefined ? 0.06 : opts.margin,
    breakLine: false,
    fit: "shrink"
  });
}

function addFormula(slide, text, x = 0.8, y = 1.45, w = 11.7, h = 0.8, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.04,
    fill: { color: opts.fill || "F7FAFC" },
    line: { color: opts.line || C.navy, pt: opts.pt || 1.1 },
    radius: 0.06
  });
  addBodyText(slide, text, x + 0.12, y + 0.08, w - 0.24, h - 0.16, {
    fontFace: "Cambria Math",
    fontSize: opts.fontSize || 21,
    align: opts.align || "center",
    valign: "mid",
    color: opts.color || C.text
  });
}

function addCallout(slide, title, text, x, y, w, h, kind = "info") {
  const palette = kind === "alert"
    ? { fill: C.paleRed, line: C.red, title: C.red }
    : kind === "warn"
      ? { fill: C.paleOrange, line: C.orange, title: C.orange }
      : { fill: C.light, line: C.teal, title: C.navy };
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    fill: { color: palette.fill },
    line: { color: palette.line, pt: 1.2 },
    radius: 0.05
  });
  addBodyText(slide, title, x + 0.14, y + 0.08, w - 0.28, 0.25, {
    fontSize: 14, bold: true, color: palette.title
  });
  addBodyText(slide, text, x + 0.14, y + 0.36, w - 0.28, h - 0.44, {
    fontSize: 14.2, color: C.text, valign: "mid"
  });
}

function addBullets(slide, bullets, x = 0.7, y = 1.0, w = 12.0, h = 5.7, opts = {}) {
  const gap = opts.gap || 0.12;
  const n = bullets.length;
  const itemH = Math.min(opts.maxItemH || 0.82, (h - gap * (n - 1)) / n);
  bullets.forEach((item, i) => {
    const text = typeof item === "string" ? item : item.text;
    const level = typeof item === "string" ? 0 : (item.level || 0);
    const color = typeof item === "string" ? C.text : (item.color || C.text);
    slide.addText(text, {
      x: x + 0.28 * level,
      y: y + i * (itemH + gap),
      w: w - 0.28 * level,
      h: itemH,
      fontFace: "Aptos",
      fontSize: opts.fontSize || 17,
      color,
      margin: 0.04,
      breakLine: false,
      valign: "mid",
      fit: "shrink",
      bullet: { type: "ul", indent: 17 + 12 * level, hanging: 4 }
    });
  });
}

function bulletSlide(title, bullets, opts = {}) {
  const slide = baseSlide(title);
  if (opts.lead) {
    addBodyText(slide, opts.lead, 0.65, 0.82, 12.05, 0.55, {
      fontSize: 17.5, color: C.muted, italic: opts.leadItalic || false
    });
  }
  const y = opts.lead ? 1.42 : 0.88;
  const h = opts.callout ? 4.65 : 5.95;
  addBullets(slide, bullets, 0.72, y, 11.95, h, {
    fontSize: opts.fontSize || 17,
    gap: opts.gap || 0.12,
    maxItemH: opts.maxItemH || 0.82
  });
  if (opts.callout) {
    addCallout(slide, opts.callout.title, opts.callout.text,
      0.72, 5.78, 11.95, 1.12, opts.callout.kind || "info");
  }
  if (opts.notes) slide.addNotes(opts.notes);
  return slide;
}

function formulaSlide(title, intro, formula, bullets = [], callout = null) {
  const slide = baseSlide(title);
  if (intro) addBodyText(slide, intro, 0.7, 0.82, 11.95, 0.5, { fontSize: 17.5 });
  addFormula(slide, formula, 0.78, 1.42, 11.8, formula.includes("\n") ? 1.35 : 0.82, {
    fontSize: formula.length > 135 ? 17 : 20
  });
  const fy = formula.includes("\n") ? 2.95 : 2.42;
  const fh = callout ? 2.75 : 3.95;
  if (bullets.length) addBullets(slide, bullets, 0.78, fy, 11.8, fh, { fontSize: 16.5, gap: 0.11 });
  if (callout) addCallout(slide, callout.title, callout.text, 0.78, 5.72, 11.8, 1.15, callout.kind || "info");
  return slide;
}

function addTable(slide, headers, rows, x, y, w, h, colW = null, fontSize = 14) {
  const data = [
    headers.map(v => ({ text: String(v), options: { bold: true, color: C.white, fill: C.navy, align: "center" } })),
    ...rows.map((row, ri) => row.map(v => ({
      text: String(v),
      options: {
        color: C.text,
        fill: ri % 2 === 0 ? "F7FAFC" : "FFFFFF",
        align: "left"
      }
    })))
  ];
  slide.addTable(data, {
    x, y, w, h,
    colW: colW || undefined,
    fontFace: "Aptos",
    fontSize,
    color: C.text,
    border: { type: "solid", color: C.line, pt: 0.65 },
    margin: 0.06,
    rowH: h / data.length,
    valign: "mid",
    autoFit: false
  });
}

function tableSlide(title, headers, rows, opts = {}) {
  const slide = baseSlide(title);
  addTable(slide, headers, rows, opts.x || 0.65, opts.y || 1.05,
    opts.w || 12.05, opts.h || 4.95, opts.colW || null, opts.fontSize || 14);
  if (opts.note) {
    addCallout(slide, opts.noteTitle || "Interpretation", opts.note,
      0.68, 6.15, 11.98, 0.75, opts.noteKind || "info");
  }
  return slide;
}

function imageSlide(title, imagePath, caption, opts = {}) {
  const slide = baseSlide(title);
  const x = opts.x || 0.55;
  const y = opts.y || 0.78;
  const w = opts.w || 12.25;
  const h = opts.h || 5.72;
  slide.addImage({
    path: imagePath, x, y, w, h,
    sizing: { type: "contain", w, h },
    altText: opts.alt || title
  });
  if (caption) addBodyText(slide, caption, 0.7, 6.54, 11.95, 0.42, {
    fontSize: 13.5, color: C.muted, align: "center", italic: true
  });
  return slide;
}

function sectionSlide(number, title, subtitle = "") {
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  addBodyText(slide, String(number) + ". " + title, 1.1, 2.65, 11.1, 0.75, {
    fontFace: "Aptos Display", fontSize: 30, bold: true, align: "center", color: C.navy
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 3.0, y: 3.56, w: 7.33, h: 0,
    line: { color: C.teal, pt: 2.2 }
  });
  if (subtitle) addBodyText(slide, subtitle, 1.5, 3.83, 10.33, 0.65, {
    fontSize: 17, color: C.muted, align: "center"
  });
  return slide;
}

function addProcessBox(slide, text, x, y, w, h, fill = C.light) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, fill: { color: fill }, line: { color: C.navy, pt: 1.1 }, radius: 0.05
  });
  addBodyText(slide, text, x + 0.08, y + 0.08, w - 0.16, h - 0.16, {
    fontSize: 14.5, bold: true, align: "center", valign: "mid"
  });
}

function addArrow(slide, x, y, w, h) {
  slide.addShape(pptx.ShapeType.chevron, {
    x, y, w, h, fill: { color: C.teal }, line: { color: C.teal }
  });
}

// 1. Title
{
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 1.25, y: 1.05, w: 10.83, h: 1.35,
    fill: { color: C.navy }, line: { color: C.navy }, radius: 0.05
  });
  addBodyText(slide, "Numerical Simulation of Financial\nStochastic Differential Equations",
    1.55, 1.27, 10.23, 0.82, {
      fontFace: "Aptos Display", fontSize: 27, bold: true, color: C.white,
      align: "center", valign: "mid"
    });
  addBodyText(slide, "From Euler–Maruyama to Nested-Grid Verification",
    1.5, 2.67, 10.33, 0.45, { fontSize: 19, color: C.teal, align: "center", bold: true });
  addBodyText(slide, "Group Members", 2.0, 3.28, 9.33, 0.32, {
    fontSize: 15.5, bold: true, align: "center", color: C.navy
  });
  addBodyText(slide,
    "Member 1: ____________________    Student ID: ____________________\n" +
    "Member 2: ____________________    Student ID: ____________________\n" +
    "Member 3: ____________________    Student ID: ____________________\n" +
    "Member 4: ____________________    Student ID: ____________________\n" +
    "Member 5: ____________________    Student ID: ____________________",
    2.0, 3.64, 9.33, 1.62, { fontSize: 13.5, align: "center", valign: "mid" });
  addBodyText(slide, "Numerical Partial Differential Equations",
    2.0, 5.52, 9.33, 0.34, { fontSize: 14, align: "center", color: C.muted });
  addBodyText(slide, "September 2026",
    2.0, 5.92, 9.33, 0.32, { fontSize: 13.5, align: "center", color: C.muted });
  slide.addShape(pptx.ShapeType.line, {
    x: 3.6, y: 6.42, w: 6.13, h: 0, line: { color: C.teal, pt: 2 }
  });
}

// 2
bulletSlide("Purpose of the Presentation", [
  "Discretise a stochastic differential equation on a time grid.",
  "Use Monte Carlo averages to estimate expectations and uncertainty.",
  "Explain the difference between Euler–Maruyama and Milstein.",
  "Distinguish strong convergence from weak convergence.",
  "Validate a solver when no exact solution is available.",
  "State clearly what the numerical evidence does and does not establish."
], {
  lead: "Audience: students familiar with elementary probability and the explicit Euler method, without prior stochastic calculus or finance.",
  fontSize: 16.5
});

// 3
{
  const slide = baseSlide("The Numerical Workflow");
  const labels = [
    "Continuous model\ndZ = a(Z)dt + b(Z)dW",
    "Time grid\ntₙ = nh",
    "Time stepping\nEM / Milstein",
    "Repeated paths\nMonte Carlo"
  ];
  labels.forEach((t, i) => {
    addProcessBox(slide, t, 0.5 + i * 3.15, 1.35, 2.6, 1.0);
    if (i < 3) addArrow(slide, 3.12 + i * 3.15, 1.68, 0.35, 0.34);
  });
  addProcessBox(slide, "Error analysis\nstrong / weak", 3.2, 3.35, 2.75, 1.0, "F7FAFC");
  addArrow(slide, 6.05, 3.68, 0.38, 0.34);
  addProcessBox(slide, "Evidence\nslopes, intervals, diagnostics", 6.55, 3.35, 3.1, 1.0, "F7FAFC");
  slide.addShape(pptx.ShapeType.downArrow, {
    x: 5.77, y: 2.48, w: 0.46, h: 0.65,
    fill: { color: C.teal }, line: { color: C.teal }
  });
  addCallout(slide, "Central numerical-analysis question",
    "A simulation is credible only when the discretisation, error reduction, statistical uncertainty, and reproducibility are explicit.",
    1.15, 5.15, 11.03, 1.15, "alert");
}

// 4
formulaSlide("Connection with Numerical PDEs",
  "For dSₜ = a(Sₜ)dt + b(Sₜ)dWₜ, define the conditional expectation",
  "u(t,s) = E[ φ(Sₜ) | Sₜ = s ]\n\nuₜ + a(s)uₛ + ½b(s)²uₛₛ = 0,      u(T,s) = φ(s)",
  [
    "PDE route: discretise the derivatives on a grid in (t,s).",
    "This coursework: discretise random paths in time and approximate the expectation by Monte Carlo."
  ],
  {
    title: "Course connection",
    text: "The central ideas remain discretisation, convergence, stable computation, and error quantification.",
    kind: "info"
  }
);

// 5
tableSlide("Two Models, Two Numerical Roles",
  ["Aspect", "Model 1: GBM benchmark", "Model 2: non-affine model"],
  [
    ["Purpose", "Exact solution for verification", "Realistic test without a closed form"],
    ["Methods", "Exact update, EM, Milstein", "Log-variable Euler–Maruyama"],
    ["Outputs", "Strong/weak errors and moments", "Nested-grid differences and nonlinear observables"],
    ["Reference", "Exact terminal value on the same path", "A much finer numerical grid"],
    ["Main issue", "Path error versus expectation error", "Error in the numerical reference"]
  ], {
    x: 0.55, y: 1.1, w: 12.25, h: 4.85, colW: [2.0, 5.05, 5.2], fontSize: 13.5,
    noteTitle: "Strategy",
    note: "Validate the implementation on an exact benchmark before using it in a model without an exact solution."
  });

// 6
bulletSlide("Structure", [
  "1. From the Euler method to stochastic time stepping",
  "2. Model 1: verification against an exact solution",
  "3. Model 2: nested-grid verification without an exact solution",
  "4. Evaluation, reproducibility, and conclusions",
  "5. Backup derivations"
], { fontSize: 20, gap: 0.23, maxItemH: 0.78 });

// 7
sectionSlide(1, "From the Euler Method to Stochastic Time Stepping",
  "Time grids, Brownian increments, Monte Carlo, and convergence");

// 8
formulaSlide("Review: Explicit Euler for an ODE",
  "For y′(t)=f(y), introduce tₙ=nh with h=T/N.",
  "y(tₙ₊₁) − y(tₙ) ≈ f(yₙ)h\n\n              yₙ₊₁ = yₙ + f(yₙ)h",
  [],
  {
    title: "Key idea",
    text: "Continuous evolution is replaced by many short steps. A smaller h usually improves the approximation at greater computational cost."
  }
);

// 9
formulaSlide("An SDE Adds a Random Increment",
  "A scalar stochastic differential equation has two contributions:",
  "dZₜ = a(Zₜ)dt + b(Zₜ)dWₜ",
  [
    "a(Zₜ)dt: drift, analogous to deterministic ODE motion.",
    "b(Zₜ)dWₜ: diffusion, representing random fluctuations.",
    "Brownian paths are not differentiable, so an ordinary Taylor expansion is insufficient."
  ],
  {
    title: "One-step viewpoint",
    text: "Freeze both coefficients at the left endpoint to obtain the basic stochastic Euler method."
  }
);

// 10
formulaSlide("Brownian Increments in the Code",
  "The program generates independent standard normal variables Zₙ.",
  "ΔWₙ = Wₜₙ₊₁ − Wₜₙ  ~  N(0,h),        ΔWₙ = √h Zₙ",
  [
    "E[ΔWₙ] = 0: positive and negative disturbances cancel on average.",
    "SD(ΔWₙ) = √h: the random increment is O(√h), not O(h)."
  ],
  {
    title: "Common error",
    text: "Using hZₙ suppresses the stochastic term too rapidly and changes the limiting model.",
    kind: "alert"
  }
);

// 11
formulaSlide("Euler–Maruyama",
  "Freeze drift and diffusion over a single time step:",
  "Zₙ₊₁ = Zₙ + a(Zₙ)h + b(Zₙ)ΔWₙ",
  [
    "The method is explicit and uses only the known state Zₙ.",
    "One increment sequence produces one approximate path.",
    "Many paths are required to estimate expectations and uncertainty."
  ]
);

// 12
formulaSlide("Monte Carlo Estimation",
  "For independent samples X⁽¹⁾,…,X⁽ᴹ⁾, estimate E[X] by",
  "m̂ᴹ = (1/M) Σᵢ X⁽ⁱ⁾,       SE(m̂ᴹ) ≈ sₓ/√M\n\n95% CI:  m̂ᴹ ± 1.96 sₓ/√M",
  [],
  {
    title: "Cost implication",
    text: "Halving the Monte Carlo standard error requires approximately four times as many paths.",
    kind: "warn"
  }
);

// 13
formulaSlide("Two Contributions to the Total Error",
  "A Monte Carlo time-stepping estimate contains two conceptually different errors:",
  "Q̂ₕ,ᴹ − Q = [ E(Qₕ) − Q ] + [ Q̂ₕ,ᴹ − E(Qₕ) ]\n\n              time-discretisation bias        sampling noise",
  [
    "Typical bias size: Chᵖ.",
    "Typical sampling error: Cᴹ M⁻¹ᐟ²."
  ],
  {
    title: "Experimental design principle",
    text: "To measure p, sampling noise must remain below the time-discretisation error over the fitted grid range."
  }
);

// 14
formulaSlide("Why Stochastic Taylor Expansions Need a Correction",
  "Itô's formula is the stochastic counterpart of the chain rule:",
  "df(Zₜ) = f′(Zₜ)dZₜ + ½ f″(Zₜ)b(Zₜ)²dt",
  [
    "ΔW = O(√h), so (ΔW)² = O(h).",
    "Some second-order random terms are as large as the deterministic drift term."
  ],
  {
    title: "Practical interpretation",
    text: "Those second-order random terms cannot be discarded in a higher-accuracy pathwise method."
  }
);

// 15
formulaSlide("Milstein: One Additional Random Second-Order Term",
  "For dZ=a(Z)dt+b(Z)dW, the scalar Milstein update is",
  "Zₙ₊₁ = Zₙ + a(Zₙ)h + b(Zₙ)ΔWₙ\n        + ½ b(Zₙ)b′(Zₙ)[(ΔWₙ)² − h]",
  [
    "The first three terms are Euler–Maruyama.",
    "The correction has zero expectation because E[(ΔW)²]=h.",
    "In scalar problems, the strong order typically rises from 1/2 to 1."
  ]
);

// 16
formulaSlide("Coupling Coarse and Fine Paths",
  "If one coarse step contains q fine steps, define",
  "ΔWᶜₖ = Σⱼ₌₁ᑫ ΔWᶠₖ,ⱼ        and        ΔWᶜₖ ~ N(0,qhᶠ)",
  [
    "Coupled comparison: both solutions use the same Brownian path.",
    "Independent comparison: the difference is dominated by two different random paths."
  ],
  {
    title: "Why coupling matters",
    text: "A strong error should isolate time-discretisation error rather than random-input differences.",
    kind: "alert"
  }
);

// 17
{
  const slide = baseSlide("Strong and Weak Errors");
  addCallout(slide, "Strong error: are paths close?",
    "e_strong(h) = E|Zᵀʰ − Zᵀ|\n\nThe numerical and exact terminal values must share the same Brownian path.",
    0.65, 1.15, 5.9, 3.55, "info");
  addCallout(slide, "Weak error: are statistics close?",
    "e_weak(h) = |E φ(Zᵀʰ) − E φ(Zᵀ)|\n\nOnly the expectation of a chosen observable is compared.",
    6.78, 1.15, 5.9, 3.55, "info");
  addCallout(slide, "They are not interchangeable",
    "A method may be inaccurate path by path while estimating a particular expectation accurately.",
    0.85, 5.25, 11.63, 1.05, "alert");
}

// 18
formulaSlide("Reading a Convergence Order",
  "If e(h) ≈ Chᵖ, take logarithms:",
  "log e ≈ log C + p log h",
  [
    "p = 1/2: halving h multiplies the error by about 0.707.",
    "p = 1: halving h multiplies the error by about 0.5.",
    "The log–log fitted slope estimates p."
  ],
  {
    title: "Caution",
    text: "Interpret the slope together with its fitting range, uncertainty, and reference-solution error.",
    kind: "warn"
  }
);

// 19
sectionSlide(2, "Model 1: Verification against an Exact Solution",
  "Geometric Brownian motion as a controlled benchmark");

// 20
formulaSlide("Geometric Brownian Motion as a Test Equation",
  "The benchmark model is",
  "dSₜ = μSₜdt + σSₜdWₜ\n\nS₀=100,   μ=0.05,   σ=0.30,   T=1",
  [
    "Drift and diffusion are proportional to the current state.",
    "The exact solution permits direct error measurement.",
    "The exact state remains positive, providing an additional diagnostic."
  ],
  {
    title: "Why start here?",
    text: "A solver should reproduce known benchmark behaviour before it is used in a model without an exact solution."
  }
);

// 21
formulaSlide("Deriving the Exact GBM Solution",
  "Apply Itô's formula to log S:",
  "d log Sₜ = (μ − ½σ²)dt + σdWₜ\n\nSₜ = S₀ exp[(μ − ½σ²)t + σWₜ]",
  [],
  {
    title: "Interpretation",
    text: "The term −σ²/2 follows from the stochastic chain rule; it is not an additional financial assumption.",
    kind: "alert"
  }
);

// 22
formulaSlide("Exact Moments as Distribution-Level Checks",
  "The terminal state is lognormal, giving",
  "E[Sᵀ] = S₀eᵘᵀ = 105.1271\nVar(Sᵀ) = S₀²e²ᵘᵀ(eˢ²ᵀ−1) = 1040.7868",
  [
    "Exact-sampling estimate of the mean: 105.1987.",
    "Exact-sampling estimate of the variance: 1045.0120.",
    "Differences are consistent with Monte Carlo sampling variation."
  ]
);

// 23
formulaSlide("Three One-Step Updates for GBM",
  "All methods use the same ΔWₙ ~ N(0,h).",
  "Exact:      Sₙ₊₁ = Sₙ exp[(μ−½σ²)h + σΔWₙ]\nEM:         Sₙ₊₁ = Sₙ(1 + μh + σΔWₙ)\nMilstein:  Sₙ₊₁ = Sₙ[1 + μh + σΔWₙ + ½σ²((ΔWₙ)²−h)]",
  [],
  {
    title: "Fair comparison",
    text: "Reusing the same increments ensures that terminal differences reflect numerical error rather than different random inputs."
  }
);

// 24
{
  const slide = baseSlide("Core GBM Implementation");
  const code = [
    "h = T / N",
    "dW = np.sqrt(h) * rng.standard_normal((M, N))",
    "",
    "S_em  = np.full(M, S0)",
    "S_mil = np.full(M, S0)",
    "for n in range(N):",
    "    dw = dW[:, n]",
    "    S_em *= 1.0 + mu*h + sigma*dw",
    "    S_mil *= (1.0 + mu*h + sigma*dw",
    "              + 0.5*sigma**2*(dw**2 - h))",
    "",
    "W_T = dW.sum(axis=1)",
    "S_exact = S0*np.exp((mu - 0.5*sigma**2)*T + sigma*W_T)"
  ].join("\n");
  slide.addText(code, {
    x: 0.65, y: 0.92, w: 12.0, h: 4.82,
    fontFace: "Aptos Mono", fontSize: 14.2, color: C.text,
    fill: { color: "F7FAFC" }, line: { color: C.line, pt: 0.9 },
    margin: 0.14, fit: "shrink", breakLine: false
  });
  addCallout(slide, "Implementation points",
    "The arrays advance M paths simultaneously, and the exact value uses the sum of the same increments.",
    0.75, 5.95, 11.82, 0.9, "info");
}

// 25
bulletSlide("GBM Experimental Protocol", [
  "T=1, grid sizes N=2ᵏ, and step size h=T/N.",
  "A fixed number of paths and a recorded random seed are used.",
  "Strong error: M⁻¹Σᵢ|Sᵀ,ᵢʰ − Sᵀ,ᵢ exact|.",
  "Standard error is computed from the pathwise absolute differences.",
  "Weak mean error is evaluated analytically whenever possible.",
  "Log–log regression is applied over a stated asymptotic range."
], {
  callout: {
    title: "Role of the random seed",
    text: "A fixed seed does not improve accuracy. It permits exact reproduction of the pseudorandom sample.",
    kind: "alert"
  },
  fontSize: 16.2
});

// 26
imageSlide("GBM Strong-Convergence Results",
  path.join(FIG, "report_gbm_strong.png"),
  "Fitted slopes: Euler–Maruyama 0.500; Milstein 0.991.",
  { alt: "Log-log strong convergence plot for GBM" });

// 27
tableSlide("Interpreting the Strong-Error Plot",
  ["Method", "N=64", "N=1024", "Reduction"],
  [
    ["Euler–Maruyama", "0.66641", "0.16658", "about 4×"],
    ["Milstein", "0.02391", "0.00153", "about 15.6×"]
  ], {
    x: 0.85, y: 1.15, w: 11.65, h: 2.0, colW: [3.3, 2.4, 2.4, 3.55], fontSize: 16,
    noteTitle: "Conclusion",
    note: "Increasing N by 16 reduces h by 16. The observed reductions agree with strong order 1/2 for EM and order 1 for Milstein."
  });

// 28
{
  const slide = baseSlide("Individual Challenge: Before and After");
  const before = path.join(IC, "figure_before_improvement.png");
  const after = path.join(IC, "figure_after_improvement.png");
  slide.addImage({ path: before, x: 0.35, y: 0.85, w: 6.2, h: 4.75, sizing: { type: "contain", w: 6.2, h: 4.75 }, altText: "Convergence figure before improvement" });
  slide.addImage({ path: after, x: 6.78, y: 0.85, w: 6.2, h: 4.75, sizing: { type: "contain", w: 6.2, h: 4.75 }, altText: "Convergence figure after improvement" });
  addBodyText(slide, "BEFORE: error curves alone", 0.65, 5.55, 5.6, 0.35, { fontSize: 15, bold: true, align: "center" });
  addBodyText(slide, "AFTER: repeated-run error bars, theory guides, fitted slopes", 6.92, 5.55, 5.75, 0.35, { fontSize: 15, bold: true, align: "center" });
  addCallout(slide, "Improvement",
    "A qualitative visual claim becomes quantitative, checkable, and reproducible evidence.",
    1.2, 6.13, 10.93, 0.74, "info");
}

// 29
formulaSlide("Analytic Weak Mean Error",
  "Euler–Maruyama satisfies E[Sₙ₊₁ | Sₙ] = Sₙ(1+μh).",
  "E[Sᴺ EM] = S₀(1+μh)ᵀᐟʰ\n\n|S₀(1+μh)ᵀᐟʰ − S₀eᵘᵀ| = O(h)",
  [
    "The Milstein correction has zero expectation.",
    "Therefore EM and Milstein have the same terminal mean and the same weak mean bias."
  ]
);

// 30
imageSlide("GBM Weak-Convergence Results",
  path.join(FIG, "report_gbm_weak.png"),
  "EM slope 0.999; Milstein slope 1.000. The curves coincide because the analytic mean bias is identical.",
  { alt: "GBM weak convergence plot" });

// 31
bulletSlide("Why Better Paths Do Not Improve This Mean", [
  "Milstein improves the agreement of each numerical path with the exact path.",
  "Its additional correction has zero expectation.",
  "For φ(S)=S, EM and Milstein therefore have identical weak errors.",
  "A different nonlinear observable may produce a different comparison."
], {
  callout: {
    title: "Orders require an error criterion",
    text: "Milstein has higher strong order in this benchmark. This does not imply higher weak order for every observable.",
    kind: "alert"
  }
});

// 32
imageSlide("Distribution Check",
  path.join(FIG, "gbm_distribution.png"),
  "The empirical distribution agrees with the exact lognormal benchmark; moments agree within sampling uncertainty.",
  { alt: "GBM distribution and moment diagnostic" });

// 33
tableSlide("Positivity Check",
  ["Terminal-value method", "Negative values / paths", "Empirical frequency"],
  [
    ["Exact update", "0 / 160000", "0.000%"],
    ["Euler–Maruyama", "0 / 160000", "0.000%"],
    ["Milstein", "0 / 160000", "0.000%"]
  ], {
    x: 1.0, y: 1.35, w: 11.33, h: 2.65, colW: [4.6, 3.5, 3.23], fontSize: 16,
    noteTitle: "Scope of the result",
    note: "This is an empirical terminal-time frequency for the reported parameters and grids, not a proof of positivity preservation.",
    noteKind: "alert"
  });

// 34
bulletSlide("What the GBM Benchmark Established", [
  "Brownian increments use the correct √h scaling.",
  "Exact and numerical values are coupled through the same path.",
  "EM and Milstein reproduce their expected strong orders.",
  "Both methods have first-order weak mean error for an analytic reason.",
  "Moment, distribution, and positivity checks support the implementation."
], {
  callout: {
    title: "Next step",
    text: "Replace the unavailable exact solution by a controlled fine-grid numerical reference."
  }
});

// 35
sectionSlide(3, "Model 2: Nested-Grid Verification without an Exact Solution",
  "State-dependent volatility, correlated noise, and a numerical reference");

// 36
formulaSlide("A Non-Affine Model with State-Dependent Volatility",
  "Let Sₜ=eˣᵗ and consider the coupled system",
  "dXₜ = [μ − ½g(Yₜ)²]dt + g(Yₜ)dWₜ⁽¹⁾\ndYₜ = κ(θ−Yₜ)dt + ξ√(1+Yₜ²)dWₜ⁽²⁾\ng(y)=0.1 + 0.4/(1+e⁻ʸ),    Corr(dW⁽¹⁾,dW⁽²⁾)=ρ",
  [
    "Y changes the noise amplitude of X.",
    "The coefficient functions are non-affine.",
    "No directly usable exact terminal solution is available."
  ]
);

// 37
tableSlide("Parameter Set",
  ["Parameter", "Numerical role", "Value"],
  [
    ["S₀, Y₀", "Initial conditions", "100, 0"],
    ["μ", "Mean growth component of X", "0.05"],
    ["κ, θ", "Mean-reversion rate and centre for Y", "2, −0.2"],
    ["ξ", "Noise scale in Y", "0.6"],
    ["ρ", "Correlation between random drivers", "−0.7"],
    ["T", "Terminal time", "1"]
  ], {
    x: 0.8, y: 1.0, w: 11.73, h: 4.9, colW: [2.0, 7.35, 2.38], fontSize: 14.5,
    noteTitle: "Minimal interpretation",
    note: "Treat S as a positive state and Y as a second state controlling its instantaneous random fluctuation."
  });

// 38
formulaSlide("Generating Correlated Brownian Increments",
  "Generate independent Z₁,Z₂ ~ N(0,1) and set",
  "ΔW₁ = √h Z₁\nΔW₂ = √h [ρZ₁ + √(1−ρ²) Z₂]\n\nVar(ΔW₁)=Var(ΔW₂)=h,      Corr(ΔW₁,ΔW₂)=ρ",
  [],
  {
    title: "Diagnostic",
    text: "Observed sample correlation: −0.699675. Target correlation: −0.7.",
    kind: "alert"
  }
);

// 39
formulaSlide("Why Discretise X = log S?",
  "A direct Euler step for S can become negative after a large negative random increment.",
  "Sₙ = exp(Xₙ) > 0",
  [
    "Update X first, then transform back to S.",
    "Positivity is automatic whenever X remains finite."
  ],
  {
    title: "Structure-aware discretisation",
    text: "The variable transformation uses analytic structure to preserve a state constraint."
  }
);

// 40
formulaSlide("Synchronous Euler–Maruyama Update",
  "Both components use the old state Yₙ:",
  "Xₙ₊₁ = Xₙ + [μ−½g(Yₙ)²]h + g(Yₙ)ΔW₁,ₙ\nYₙ₊₁ = Yₙ + κ(θ−Yₙ)h + ξ√(1+Yₙ²)ΔW₂,ₙ\nSₙ₊₁ = exp(Xₙ₊₁)",
  [],
  {
    title: "Meaning of synchronous",
    text: "Updating Y first and using the new value in the X step would implement a different numerical scheme.",
    kind: "alert"
  }
);

// 41
{
  const slide = baseSlide("Implementation Details");
  const code = [
    "def g(y):",
    "    # stable sigmoid avoids exponential overflow",
    "    return 0.1 + 0.4 * expit(y)",
    "",
    "for n in range(N):",
    "    y_old = y.copy()",
    "    gy = g(y_old)",
    "    x += (mu - 0.5*gy**2)*h + gy*dW1[:, n]",
    "    y += kappa*(theta - y_old)*h \\",
    "         + xi*np.sqrt(1.0 + y_old**2)*dW2[:, n]",
    "",
    "assert np.isfinite(x).all() and np.isfinite(y).all()",
    "s = np.exp(x)"
  ].join("\n");
  slide.addText(code, {
    x: 0.65, y: 0.92, w: 12.0, h: 4.9,
    fontFace: "Aptos Mono", fontSize: 14.3, color: C.text,
    fill: { color: "F7FAFC" }, line: { color: C.line, pt: 0.9 },
    margin: 0.14, fit: "shrink", breakLine: false
  });
  addCallout(slide, "Recorded diagnostics",
    "Finite-state checks, increment variances, correlation, and the number of non-positive prices.",
    0.75, 6.0, 11.82, 0.85, "info");
}

// 42
formulaSlide("An Exact Structural Property of the Discrete Mean",
  "Conditional on the current state, use E[eᵃΔᵂ] = eᵃ²ʰᐟ²:",
  "E[Sₙ₊₁ | 𝓕ₙ] = Sₙe⁽ᵘ⁻½ᵍₙ²⁾ʰ E[eᵍₙΔᵂ]\n               = Sₙeᵘʰ\n\nE[Sᴺ] = S₀eᵘᵀ  for every h",
  [],
  {
    title: "Consequence for weak testing",
    text: "The observable φ(S)=S has zero discretisation bias and cannot test whether the terminal distribution is correct.",
    kind: "alert"
  }
);

// 43
formulaSlide("Why Use a Call Payoff as the Nontrivial Observable?",
  "Choose a nonlinear terminal observable",
  "φ(S) = (S−K)⁺ = max(S−K,0),       K=100",
  [
    "E[φ(S)] is not determined by E[S].",
    "Equal means do not imply equal payoff expectations.",
    "The observable detects changes in distribution shape and the upper tail.",
    "Its kink at S=K makes a weak rate harder to resolve."
  ],
  {
    title: "Reason for the choice",
    text: "Once the linear mean is exact, a distribution-sensitive observable is required."
  }
);

// 44
formulaSlide("Nested Fine-Grid Reference",
  "Construct a coarse and a fine solution from the same finest Brownian increments:",
  "D̂ᴺ = (1/M)Σᵢ |Sᵀ,ᵢᴺ − Sᵀ,ᵢ ref|\n\nB̂ᴺ = (1/M)Σᵢ [φ(Sᵀ,ᵢᴺ) − φ(Sᵀ,ᵢ ref)]",
  [
    "The first quantity is a coupled strong difference.",
    "The second is a paired weak-observable difference."
  ],
  {
    title: "Precise terminology",
    text: "These are differences relative to a numerical reference, not known exact errors. Reference sensitivity must be checked.",
    kind: "alert"
  }
);

// 45
tableSlide("Nested-Grid Experimental Design",
  ["Component", "Setting"],
  [
    ["Coarse grids", "N = 8, 16, 32, 64, 128, 256"],
    ["Main reference", "N_ref = 8192"],
    ["Sensitivity references", "2048, 4096, 8192"],
    ["Number of paths", "M = 100000"],
    ["Coupling", "All grids aggregate the same finest increments"],
    ["Strong quantity", "E|Sᵀᴺ − Sᵀ ref|"],
    ["Weak quantities", "Mean and paired call-payoff differences"]
  ], {
    x: 1.0, y: 0.92, w: 11.33, h: 5.55, colW: [3.3, 8.03], fontSize: 14,
    noteTitle: "Fitting range",
    note: "The strong-rate fit uses N=8,16,32,64 to reduce finite-reference curvature."
  });

// 46
imageSlide("Non-Affine Strong-Difference Results",
  path.join(FIG, "report_nonaffine_strong.png"),
  "The fitted slope relative to N_ref=8192 is 0.491, consistent with EM strong order 1/2.",
  { alt: "Nested-grid strong convergence for the non-affine model" });

// 47
tableSlide("Reference-Grid Sensitivity",
  ["N_ref", "Fitted slope", "Interpretation"],
  [
    ["2048", "0.496", "Coarser reference, similar slope"],
    ["4096", "0.493", "Close to the finer result"],
    ["8192", "0.491", "Main reported reference"]
  ], {
    x: 1.0, y: 1.25, w: 11.33, h: 2.85, colW: [2.2, 2.8, 6.33], fontSize: 16,
    noteTitle: "Supported conclusion",
    note: "The half-order trend is stable across these reference choices. This is numerical evidence, not an exact error bound."
  });

// 48
formulaSlide("The Reference Also Has Discretisation Error",
  "Differences between successive reference levels are",
  "E|S²⁰⁴⁸ − S⁴⁰⁹⁶| ≈ 0.05679\nE|S⁴⁰⁹⁶ − S⁸¹⁹²| ≈ 0.04016\n\n0.04016 / 0.05679 ≈ 0.707 ≈ 2⁻¹ᐟ²",
  [
    "The reference levels themselves show half-order reduction.",
    "The 8192-step solution is not exact.",
    "It is sufficiently fine to reveal a stable slope for N=8 to 64."
  ]
);

// 49
imageSlide("Non-Affine Weak Differences",
  path.join(FIG, "report_nonaffine_weak.png"),
  "Coarse payoff differences are resolved; fine-grid confidence intervals include zero.",
  { alt: "Weak paired differences and confidence intervals for the non-affine model" });

// 50
bulletSlide("Why No Reliable Weak Order Is Reported", [
  "For N=8,16,32, paired-payoff confidence intervals exclude zero.",
  "For N=64,128,256, the intervals include zero.",
  "At fine levels, the sign and magnitude are sensitive to sampling noise.",
  "A log–log fit would mistake noise for an asymptotic law.",
  "The kink in the payoff makes the asymptotic regime harder to resolve."
], {
  callout: {
    title: "Correct interpretation",
    text: "Weak differences decrease, but the sample budget is insufficient for a credible weak-order estimate. This limits the evidence; it does not show scheme failure.",
    kind: "alert"
  },
  fontSize: 16
});

// 51
tableSlide("Sample-Size Experiment",
  ["M", "Paired difference", "Standard error", "95% interval"],
  [
    ["10,000", "0.009045", "0.005149", "[−0.001048, 0.019137]"],
    ["40,000", "0.004942", "0.002592", "[−0.000139, 0.010022]"],
    ["100,000", "0.001722", "0.001633", "[−0.001479, 0.004923]"]
  ], {
    x: 0.65, y: 1.2, w: 12.05, h: 2.85, colW: [2.0, 3.0, 2.8, 4.25], fontSize: 15.5,
    noteTitle: "Interpretation",
    note: "Standard error decreases approximately as M⁻¹ᐟ², but all three intervals still include zero.",
    noteKind: "warn"
  });

// 52
formulaSlide("Mean and Implementation Diagnostics",
  "The exact discrete-mean identity predicts",
  "E[Sᵀᴺ] = 100e⁰·⁰⁵ = 105.1271\n\nSimulation: 105.08796,    95% CI [104.89962, 105.27629]\nPayoff: 14.53804,          95% CI [14.40515, 14.67093]",
  [],
  {
    title: "Different roles",
    text: "The mean checks the implementation; the nonlinear payoff probes distributional weak error."
  }
);

// 53
tableSlide("Numerical Diagnostic Checklist",
  ["Diagnostic", "Observation"],
  [
    ["Increment variances", "Consistent with 1/8192 ≈ 1.221×10⁻⁴"],
    ["Increment correlation", "−0.699675; target −0.7"],
    ["Finite states", "All reported X, Y, and S values were finite"],
    ["Positivity", "S=exp(X) remained positive"],
    ["Exact mean identity", "The theoretical mean lies inside the empirical interval"],
    ["Reference sensitivity", "Three reference grids give similar strong slopes"]
  ], {
    x: 0.75, y: 1.0, w: 11.83, h: 4.95, colW: [3.4, 8.43], fontSize: 14.3,
    noteTitle: "Principle",
    note: "A visually convincing convergence plot does not replace these diagnostics."
  });

// 54
sectionSlide(4, "Evaluation, Reproducibility, and Conclusions",
  "What the evidence supports and how the result can be audited");

// 55
tableSlide("What the Coursework Requires",
  ["Component", "Required task", "Evidence reported"],
  [
    ["GBM strong", "Compare EM/Milstein with theory", "Slopes 0.500 and 0.991"],
    ["GBM weak", "Choose and explain an observable", "Analytic first-order mean bias"],
    ["Diagnostics", "Distribution and positivity checks", "Moments, histogram, frequency"],
    ["Non-affine strong", "Nested grids and sensitivity", "Stable half-order trend"],
    ["Non-affine weak", "Intervals and justified conclusion", "Trend visible; rate unresolved"],
    ["Reproducibility", "Commands, seed, environment, Git", "Traceable code and outputs"]
  ], {
    x: 0.45, y: 0.92, w: 12.43, h: 5.35, colW: [2.55, 4.4, 5.48], fontSize: 12.7,
    noteTitle: "Weak order",
    note: "The requirement is a sound experiment and evidence-based interpretation, not a forced slope from unresolved data.",
    noteKind: "alert"
  });

// 56
bulletSlide("Code Structure Mirrors the Mathematics", [
  "Parameters: initial data, coefficients, T, grids, paths, and seed.",
  "Random increments: finest-grid normal samples and correlation transform.",
  "Solvers: EM, Milstein, and log-variable EM.",
  "Coupling: aggregation of fine increments for each coarse grid.",
  "Statistics: means, standard errors, intervals, and fitted slopes.",
  "Outputs: tables, figures, data, and run metadata."
], {
  callout: {
    title: "Practical benefit",
    text: "An anomalous plot can be traced through statistic, path, increment, and parameter layers."
  },
  fontSize: 16.2
});

// 57
{
  const slide = baseSlide("A Minimal Reproducibility Chain");
  const steps = [
    "Identify the Git commit",
    "Run the recorded command",
    "Fix the seed and record versions",
    "Save raw output and figure data",
    "Match the reported precision"
  ];
  steps.forEach((t, i) => {
    addProcessBox(slide, t, 3.15, 0.92 + i * 1.05, 7.03, 0.65, i % 2 ? "F7FAFC" : C.light);
    if (i < steps.length - 1) {
      slide.addShape(pptx.ShapeType.downArrow, {
        x: 6.43, y: 1.60 + i * 1.05, w: 0.45, h: 0.30,
        fill: { color: C.teal }, line: { color: C.teal }
      });
    }
  });
  addCallout(slide, "Audit rule",
    "If script output and the report disagree, correct the report or identify the version difference.",
    1.05, 6.16, 11.23, 0.72, "alert");
}

// 58
bulletSlide("Eight Common Failure Modes", [
  "Using hZ instead of √h Z for Brownian increments.",
  "Comparing independent paths when measuring strong error.",
  "Confusing sample standard deviation with standard error.",
  "Refining h without checking the Monte Carlo noise floor.",
  "Updating Y before the synchronous X update.",
  "Describing a finite fine-grid solution as exact.",
  "Fitting a weak rate to differences whose intervals include zero.",
  "Reporting a slope without the fitting range and diagnostics."
], { fontSize: 15.4, gap: 0.05, maxItemH: 0.66 });

// 59
bulletSlide("How to Read a Convergence Plot Critically", [
  "Is the horizontal axis h, N, or computational cost?",
  "Is the vertical quantity an exact error or a reference difference?",
  "Are coarse and fine solutions driven by the same random input?",
  "Do error bars show standard deviation, standard error, or confidence intervals?",
  "Which points are used in the slope fit, and why?",
  "Do the finest points reach a noise or reference-error floor?",
  "Is the conclusion stable under changes in sample size or reference grid?"
], {
  callout: {
    title: "Practical rule",
    text: "Identify what the vertical axis measures before assessing linearity or reading a slope.",
    kind: "alert"
  },
  fontSize: 15.3,
  gap: 0.05
});

// 60
bulletSlide("Main Conclusions", [
  "EM and Milstein show GBM strong orders close to 1/2 and 1.",
  "For the terminal mean, both methods share the same first-order weak bias.",
  "Nested-grid experiments support half-order strong convergence in the non-affine model.",
  "The non-affine discretisation preserves the mean exactly, so a nonlinear observable is required.",
  "The present path budget supports a decreasing weak-difference trend, but not a credible weak order.",
  "Confidence intervals, reference sensitivity, and diagnostics are as important as fitted slopes."
], { fontSize: 16.1, gap: 0.11 });

// 61
bulletSlide("Possible Extensions", [
  "Increase paired samples or use a control variate for payoff differences.",
  "Balance h and M under a fixed computational budget.",
  "Refine the reference grid and quantify its systematic contribution.",
  "Report uncertainty in the fitted convergence slope.",
  "Compare Monte Carlo with a finite-difference solution of the associated backward PDE."
], {
  callout: {
    title: "Scope",
    text: "The present coursework should first explain its existing evidence and limitations clearly before adding further machinery."
  }
});

// 62
{
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  addBodyText(slide, "Thank you", 2.0, 2.0, 9.33, 0.8, {
    fontFace: "Aptos Display", fontSize: 36, bold: true, align: "center", color: C.navy
  });
  addBodyText(slide, "Questions?", 2.0, 3.0, 9.33, 0.55, {
    fontSize: 24, align: "center", color: C.text
  });
  addBodyText(slide,
    "Starting from the Euler method, three additions were essential:\nnormal increments, repeated sampling, and quantified uncertainty.",
    2.0, 4.15, 9.33, 1.0, { fontSize: 17.5, align: "center", color: C.teal, bold: true });
  slide.addShape(pptx.ShapeType.line, {
    x: 3.6, y: 5.65, w: 6.13, h: 0, line: { color: C.teal, pt: 2 }
  });
}

// 63
sectionSlide(5, "Backup Derivations", "Additional detail for questions");

// 64
formulaSlide("Backup: Why Is the GBM Mean Bias First Order?",
  "Let N=T/h and expand the logarithm:",
  "log(1+μh) = μh − ½μ²h² + O(h³)\n\n(1+μh)ᵀᐟʰ = eᵘᵀ[1 − ½μ²Th + O(h²)]\n\nS₀(1+μh)ᵀᐟʰ − S₀eᵘᵀ = O(h)",
  []
);

// 65
formulaSlide("Backup: Why Pairing Reduces Noise",
  "For two observables A and B on the same path,",
  "Var(A−B) = Var(A) + Var(B) − 2Cov(A,B)",
  [
    "A shared Brownian path makes A and B strongly positively correlated.",
    "Common path fluctuations cancel in the paired difference.",
    "The remaining variation is mainly the discretisation difference."
  ]
);

// 66
formulaSlide("Backup: Standard Error and Sample Size",
  "For paired samples D₁,…,Dᴹ,",
  "D̄ = (1/M)ΣᵢDᵢ,      SE(D̄)=sᴰ/√M\n\nM₂ ≈ M₁(ε₁/ε₂)²",
  [
    "Reducing the standard error by a factor of five requires approximately 25 times as many paths."
  ]
);

// 67
tableSlide("Backup: Terminology",
  ["Term", "Meaning in this coursework"],
  [
    ["Drift", "Deterministic mean change per unit time"],
    ["Diffusion", "Amplitude of the random fluctuation"],
    ["Brownian increment", "Normal variable with mean 0 and variance h"],
    ["Path", "A complete sequence Z₀,Z₁,…,Zᴺ"],
    ["Observable", "A terminal function φ(Zᵀ)"],
    ["Strong convergence", "Numerical and exact values approach on the same path"],
    ["Weak convergence", "Expectations of an observable approach"],
    ["Nested grid", "Coarse increments are sums of shared fine increments"],
    ["Numerical reference", "Fine-grid approximation used for an unknown exact solution"]
  ], {
    x: 0.65, y: 0.82, w: 12.03, h: 5.98, colW: [3.25, 8.78], fontSize: 13.2
  });

// 68
{
  const slide = baseSlide("References and Project Files");
  addBodyText(slide,
    "Course Problem Pack, Direction 4: Financial SDEs, pp. 6–7.",
    0.75, 1.0, 11.8, 0.55, { fontSize: 18, bold: true, color: C.navy });
  addBodyText(slide,
    "D. J. Higham, “An Algorithmic Introduction to Numerical Simulation of Stochastic Differential Equations,” SIAM Review, 43(3), 2001.",
    0.75, 1.85, 11.8, 0.85, { fontSize: 17 });
  addBodyText(slide,
    "P. E. Kloeden and E. Platen, Numerical Solution of Stochastic Differential Equations, Springer, 1992.",
    0.75, 2.9, 11.8, 0.75, { fontSize: 17 });
  addCallout(slide, "Project files",
    "gbm.py, nonaffine.py, results/, undergraduate_revision/, and presentation/.",
    0.75, 4.15, 11.8, 1.0, "info");
  addCallout(slide, "Editable format",
    "All titles, body text, tables, flow diagrams, and formula text in this deck are native PowerPoint objects.",
    0.75, 5.55, 11.8, 1.0, "warn");
}

pptx.writeFile({ fileName: OUT })
  .then(() => console.log("Wrote " + OUT + " with " + pptx._slides.length + " slides."))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
