<template>
  <span v-if="level" class="badge" :class="level">{{ labels[level] }}</span>
  <span v-else class="muted">—</span>
</template>

<script setup>
defineProps({ level: { type: String, default: null } });
const labels = { bajo: "Bajo", medio: "Medio", alto: "Alto" };
</script>
