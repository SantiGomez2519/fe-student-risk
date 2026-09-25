<template>
  <div>
    <h2>Estudiantes</h2>

    <div class="filters">
      <input v-model="search" placeholder="Buscar por nombre o programa…" @input="debouncedLoad" />
      <select v-model="level" @change="load">
        <option value="">Todos los niveles</option>
        <option value="bajo">Bajo</option>
        <option value="medio">Medio</option>
        <option value="alto">Alto</option>
      </select>
      <select v-model="program" @change="load">
        <option value="">Todos los programas</option>
        <option v-for="p in programs" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <div class="panel">
      <p v-if="loading" class="muted">Cargando…</p>
      <table v-else>
        <thead>
          <tr>
            <th @click="sort('full_name')">Nombre</th>
            <th>Programa</th>
            <th>Semestre</th>
            <th>Sexo</th>
            <th @click="sort('result__total_pct')">Riesgo (%)</th>
            <th>Nivel</th>
            <th>Alertas</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.id">
            <td><router-link :to="`/estudiantes/${s.id}`">{{ s.full_name }}</router-link></td>
            <td>{{ s.program }}</td>
            <td>{{ s.semester }}</td>
            <td>{{ s.sex }}</td>
            <td>{{ s.total_pct != null ? Math.round(s.total_pct * 100) + "%" : "—" }}</td>
            <td><RiskBadge :level="s.level" /></td>
            <td>
              <span v-if="s.alerts_count" class="alert-chip">⚠ {{ s.alerts_count }}</span>
              <span v-else class="muted">—</span>
            </td>
          </tr>
          <tr v-if="!students.length"><td colspan="7" class="muted">Sin resultados.</td></tr>
        </tbody>
      </table>
      <p class="muted" style="margin-top: 12px">{{ count }} estudiantes</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import RiskBadge from "../components/RiskBadge.vue";

const students = ref([]);
const count = ref(0);
const programs = ref([]);
const loading = ref(true);
const search = ref("");
const level = ref("");
const program = ref("");
const ordering = ref("-result__total_pct");

async function load() {
  loading.value = true;
  const params = { ordering: ordering.value };
  if (search.value) params.search = search.value;
  if (level.value) params.result__level = level.value;
  if (program.value) params.program = program.value;
  const data = await api.students(params);
  students.value = data.results;
  count.value = data.count;
  loading.value = false;
}

function sort(field) {
  ordering.value = ordering.value === field ? "-" + field : field;
  load();
}

let t;
function debouncedLoad() {
  clearTimeout(t);
  t = setTimeout(load, 300);
}

onMounted(async () => {
  await load();
  // build program list from an unfiltered fetch
  const all = await api.students({ ordering: "full_name" });
  programs.value = [...new Set(all.results.map((s) => s.program).filter(Boolean))].sort();
});
</script>
