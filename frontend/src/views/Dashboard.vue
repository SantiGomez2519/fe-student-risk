<template>
  <div>
    <h2>Dashboard</h2>
    <p v-if="loading" class="muted">Cargando…</p>
    <p v-else-if="error" class="muted">No se pudo cargar. ¿Está corriendo el backend? {{ error }}</p>

    <template v-else-if="data">
      <div class="cards">
        <div class="card">
          <div class="value">{{ data.total_students }}</div>
          <div class="label">Estudiantes</div>
        </div>
        <div class="card">
          <div class="value" style="color: var(--bajo)">{{ data.by_level.bajo }}</div>
          <div class="label">Riesgo bajo</div>
        </div>
        <div class="card">
          <div class="value" style="color: var(--medio)">{{ data.by_level.medio }}</div>
          <div class="label">Riesgo medio</div>
        </div>
        <div class="card">
          <div class="value" style="color: var(--alto)">{{ data.by_level.alto }}</div>
          <div class="label">Riesgo alto</div>
        </div>
        <div class="card">
          <div class="value">{{ data.students_with_alerts }}</div>
          <div class="label">Con alertas</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="panel">
          <h3>Distribución por nivel de riesgo</h3>
          <div class="chart-box"><Doughnut :data="levelChart" :options="baseOpts" /></div>
        </div>
        <div class="panel">
          <h3>Riesgo promedio por dimensión (%)</h3>
          <div class="chart-box"><Bar :data="dimChart" :options="pctOpts" /></div>
        </div>
      </div>

      <div class="panel">
        <h3>Nivel de riesgo por programa</h3>
        <div class="chart-box"><Bar :data="programChart" :options="stackedOpts" /></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Doughnut, Bar } from "vue-chartjs";
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement,
} from "chart.js";
import api from "../api";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const data = ref(null);
const loading = ref(true);
const error = ref(null);

const COLORS = { bajo: "#22c55e", medio: "#f59e0b", alto: "#ef4444" };

onMounted(async () => {
  try {
    data.value = await api.summary();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
});

const levelChart = computed(() => ({
  labels: ["Bajo", "Medio", "Alto"],
  datasets: [{
    data: [data.value.by_level.bajo, data.value.by_level.medio, data.value.by_level.alto],
    backgroundColor: [COLORS.bajo, COLORS.medio, COLORS.alto],
  }],
}));

const dimChart = computed(() => ({
  labels: data.value.dimensions.map((d) => d.dimension),
  datasets: [{
    label: "Riesgo promedio",
    data: data.value.dimensions.map((d) => Math.round(d.avg_pct * 100)),
    backgroundColor: "#38bdf8",
  }],
}));

const programChart = computed(() => ({
  labels: data.value.by_program.map((p) => p.key),
  datasets: [
    { label: "Bajo", data: data.value.by_program.map((p) => p.bajo), backgroundColor: COLORS.bajo, stack: "s" },
    { label: "Medio", data: data.value.by_program.map((p) => p.medio), backgroundColor: COLORS.medio, stack: "s" },
    { label: "Alto", data: data.value.by_program.map((p) => p.alto), backgroundColor: COLORS.alto, stack: "s" },
  ],
}));

const gridColor = "rgba(148,163,184,0.15)";
const tick = { color: "#94a3b8" };
const baseOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#e2e8f0" } } } };
const pctOpts = {
  ...baseOpts,
  scales: { y: { beginAtZero: true, max: 100, ticks: tick, grid: { color: gridColor } }, x: { ticks: tick, grid: { color: gridColor } } },
  plugins: { legend: { display: false } },
};
const stackedOpts = {
  ...baseOpts,
  scales: { x: { stacked: true, ticks: tick, grid: { color: gridColor } }, y: { stacked: true, beginAtZero: true, ticks: tick, grid: { color: gridColor } } },
};
</script>
