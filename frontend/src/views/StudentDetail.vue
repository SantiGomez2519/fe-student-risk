<template>
  <div>
    <router-link to="/estudiantes">← Volver</router-link>
    <p v-if="loading" class="muted">Cargando…</p>

    <template v-else-if="student">
      <h2>{{ student.full_name }}</h2>
      <div class="cards">
        <div class="card"><div class="value"><RiskBadge :level="student.result?.level" /></div><div class="label">Nivel de riesgo</div></div>
        <div class="card"><div class="value">{{ pct(student.result?.total_pct) }}</div><div class="label">Riesgo global</div></div>
        <div class="card"><div class="value">{{ student.result?.total }}/{{ student.result?.total_max }}</div><div class="label">Puntaje</div></div>
        <div class="card"><div class="value">{{ student.program }}</div><div class="label">Programa · Sem {{ student.semester }}</div></div>
      </div>

      <div v-if="student.result?.alerts?.length" class="panel" style="border-color: var(--alto)">
        <h3 style="color: var(--alto)">⚠ Alertas</h3>
        <span v-for="(a, i) in student.result.alerts" :key="i" class="alert-chip">
          {{ a.label }} — “{{ a.raw }}”
        </span>
      </div>

      <div class="grid-2">
        <div class="panel">
          <h3>Perfil por dimensión</h3>
          <div class="chart-box"><Radar :data="radar" :options="radarOpts" /></div>
        </div>
        <div class="panel">
          <h3>Detalle por dimensión</h3>
          <table>
            <thead><tr><th>Dimensión</th><th>Puntaje</th><th>%</th><th>Nivel</th></tr></thead>
            <tbody>
              <tr v-for="d in student.result?.dimensions" :key="d.dimension">
                <td>{{ d.dimension }}</td>
                <td>{{ d.score }}/{{ d.max }}</td>
                <td>{{ Math.round(d.pct * 100) }}%</td>
                <td><RiskBadge :level="d.level" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <h3>Respuestas por ítem</h3>
        <table>
          <thead><tr><th>Ítem</th><th>Dimensión</th><th>Respuesta</th><th>Puntaje</th></tr></thead>
          <tbody>
            <tr v-for="(it, i) in student.result?.items" :key="i">
              <td>{{ it.label }}</td>
              <td><span class="chip">{{ it.dimension }}</span></td>
              <td>{{ it.raw ?? "—" }}</td>
              <td>{{ it.value ?? "—" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Radar } from "vue-chartjs";
import {
  Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend,
} from "chart.js";
import api from "../api";
import RiskBadge from "../components/RiskBadge.vue";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const props = defineProps({ id: { type: [String, Number], required: true } });
const student = ref(null);
const loading = ref(true);

const pct = (v) => (v != null ? Math.round(v * 100) + "%" : "—");

onMounted(async () => {
  student.value = await api.student(props.id);
  loading.value = false;
});

const radar = computed(() => ({
  labels: student.value.result.dimensions.map((d) => d.dimension),
  datasets: [{
    label: "Riesgo (%)",
    data: student.value.result.dimensions.map((d) => Math.round(d.pct * 100)),
    backgroundColor: "rgba(56,189,248,0.25)",
    borderColor: "#38bdf8",
    pointBackgroundColor: "#38bdf8",
  }],
}));

const radarOpts = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      beginAtZero: true, max: 100,
      angleLines: { color: "rgba(148,163,184,0.2)" },
      grid: { color: "rgba(148,163,184,0.2)" },
      pointLabels: { color: "#e2e8f0" },
      ticks: { color: "#94a3b8", backdropColor: "transparent" },
    },
  },
  plugins: { legend: { labels: { color: "#e2e8f0" } } },
};
</script>
