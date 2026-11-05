"use strict";

const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

async function extractImage(input) {
  const file = input.files && input.files[0];
  const target = document.getElementById(input.dataset.ocrTarget);
  const status = document.getElementById(`${input.id}-status`);
  if (!file || !target || !status) return;

  if (file.size > MAX_IMAGE_BYTES) {
    status.textContent = "A imagem excede o limite de 8 MB.";
    status.className = "file-status error";
    input.value = "";
    return;
  }

  status.textContent = "Extraindo texto localmente…";
  status.className = "file-status loading";
  const body = new FormData();
  body.append("image", file);

  try {
    const response = await fetch("/api/ocr", { method: "POST", body });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Não foi possível ler a imagem.");
    target.value = result.text;
    updateEvidenceCount();
    status.textContent = "Texto extraído. Revise o campo antes de analisar.";
    status.className = "file-status success";
  } catch (error) {
    status.textContent = error.message || "Não foi possível ler a imagem.";
    status.className = "file-status error";
  }
}

document.querySelectorAll("[data-ocr-target]").forEach((input) => {
  input.addEventListener("change", () => extractImage(input));
});

const qrInput = document.getElementById("qr-image");
if (qrInput) qrInput.addEventListener("change", async () => {
  const file = qrInput.files && qrInput.files[0];
  const status = document.getElementById("qr-status");
  if (!file) return;
  status.className = "file-status";
  if (file.size > MAX_IMAGE_BYTES) {
    status.textContent = "A imagem excede o limite de 8 MB.";
    status.className = "file-status error";
    qrInput.value = "";
    return;
  }
  status.textContent = "Lendo QR Code localmente…";
  try {
    const body = new FormData();
    body.append("image", file);
    const response = await fetch("/api/qr", { method: "POST", body });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Não foi possível ler o QR Code.");
    const target = document.getElementById(result.kind === "pix" ? "pix" : "link");
    target.value = result.text;
    target.focus();
    status.textContent = "QR Code lido. Revise o conteúdo preenchido antes de conferir.";
    status.className = "file-status success";
  } catch (error) {
    status.textContent = error.message;
    status.className = "file-status error";
  }
});

const analysisForm = document.getElementById("analysis-form");
if (analysisForm) analysisForm.addEventListener("submit", () => {
  const button = analysisForm.querySelector('button[type="submit"]');
  button.disabled = true;
  button.textContent = "Conferindo…";
});

function updateEvidenceCount() {
  const counter = document.getElementById("evidence-count");
  if (!counter) return;
  const count = ["original-text", "received-text"].filter((id) => document.getElementById(id).value.trim()).length;
  counter.textContent = `${String(count).padStart(2, "0")} / 02`;
}
document.querySelectorAll("#original-text, #received-text").forEach((field) => field.addEventListener("input", updateEvidenceCount));
updateEvidenceCount();

const exampleButton = document.getElementById("fill-example");
if (exampleButton) {
  exampleButton.addEventListener("click", () => {
    document.getElementById("original-text").value = "Notebook anunciado por R$ 1.850,00. Pagamento na retirada para Loja Horizonte.";
    document.getElementById("received-text").value = "Faça um Pix de R$ 2.150,00 agora para garantir. Não conte para ninguém e envie o código de verificação.";
    document.getElementById("link").value = "bit.ly/pagamento-notebook";
    document.getElementById("expected-recipient").value = "Loja Horizonte";
    document.getElementById("displayed-recipient").value = "Carlos da Silva";
    const paymentDetails = document.querySelector(".payment-details");
    if (paymentDetails) paymentDetails.open = true;
    updateEvidenceCount();
    document.getElementById("original-text").focus();
  });
}

const printButton = document.getElementById("print-result");
if (printButton) printButton.addEventListener("click", () => window.print());

const clearForm = document.querySelector("[data-confirm-clear]");
if (clearForm) {
  clearForm.addEventListener("submit", (event) => {
    if (!window.confirm("Apagar todo o histórico local? Esta ação não pode ser desfeita.")) event.preventDefault();
  });
}

if (document.getElementById("resultado")) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.getElementById("resultado").scrollIntoView({ behavior: reducedMotion ? "instant" : "smooth", block: "start" });
}
