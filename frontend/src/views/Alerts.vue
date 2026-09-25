<template>
  <div>
    <h2>Alertas</h2>
    <p class="muted">Estudiantes con ítems críticos que requieren atención prioritaria.</p>
    <div class="panel">
      <p v-if="loading" class="muted">Cargando…</p>
      <table v-else>
        <thead>
          <tr><th>Estudiante</th><th>Programa</th><th>Nivel</th><th>Alertas</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in alerts" :key="a.id">
            <td><router-link :to="`/estudiantes/${a.id}`">{{ a.full_name }}</router-link></td>
            <td>{{ a.program }}</td>
            <td><RiskBadge :level="a.level" /></td>
            <td>
              <span v-for="(x, i) in a.alerts" :key="i" class="alert-chip">{{ x.label }}</span>
            </td>
          </tr>
          <tr v-if="!alerts.length"><td colspan="4" class="muted">Sin alertas 🎉</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import RiskBadge from "../components/RiskBadge.vue";

const alerts = ref([]);
const loading = ref(true);
onMounted(async () => {
  alerts.value = await api.alerts();
  loading.value = false;
});
</script>
