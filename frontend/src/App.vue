<template>
  <div class="layout">
    <aside class="sidebar">
      <h1>🎓 Riesgo Estudiantil</h1>
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/estudiantes">Estudiantes</router-link>
        <router-link to="/alertas">Alertas</router-link>
        <router-link to="/cargar">Cargar Excel</router-link>
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>
