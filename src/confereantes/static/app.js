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

const exampleButton = document.getElementById("fill-example");
if (exampleButton) {
  exampleButton.addEventListener("click", () => {
    document.getElementById("original-text").value = "Notebook anunciado por R$ 1.850,00. Pagamento na retirada para Loja Horizonte.";
    document.getElementById("received-text").value = "Faça um Pix de R$ 2.150,00 agora para garantir. Não conte para ninguém e envie o código de verificação.";
    document.getElementById("link").value = "bit.ly/pagamento-notebook";
    document.getElementById("expected-recipient").value = "Loja Horizonte";
    document.getElementById("displayed-recipient").value = "Carlos da Silva";
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
  document.getElementById("resultado").scrollIntoView({ behavior: "smooth", block: "start" });
}
