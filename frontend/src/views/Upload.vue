<template>
  <div>
    <h2>Cargar Excel</h2>
    <p class="muted">
      Sube el archivo de respuestas del formulario (hoja <code>Form Responses 1</code>).
      Se recalcularán todos los resultados de riesgo.
    </p>
    <div class="panel">
      <input type="file" accept=".xlsx" @change="onFile" />
      <p v-if="file" class="muted" style="margin-top: 10px">Archivo: {{ file.name }}</p>
      <div style="margin-top: 14px">
        <button :disabled="!file || busy" @click="submit">
          {{ busy ? "Procesando…" : "Cargar y analizar" }}
        </button>
      </div>
      <p v-if="result" style="color: var(--bajo); margin-top: 14px">
        ✓ Listo. Filas: {{ result.rows }} · creados: {{ result.created }} · actualizados: {{ result.updated }}
      </p>
      <p v-if="error" style="color: var(--alto); margin-top: 14px">✗ {{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";

const file = ref(null);
const busy = ref(false);
const result = ref(null);
const error = ref(null);

function onFile(e) {
  file.value = e.target.files[0] || null;
  result.value = null;
  error.value = null;
}

async function submit() {
  busy.value = true;
  result.value = null;
  error.value = null;
  try {
    result.value = await api.upload(file.value);
  } catch (e) {
    error.value = e.response?.data?.detail || e.message;
  } finally {
    busy.value = false;
  }
}
</script>
