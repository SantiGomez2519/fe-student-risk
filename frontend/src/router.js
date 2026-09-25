import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./views/Dashboard.vue";
import Students from "./views/Students.vue";
import StudentDetail from "./views/StudentDetail.vue";
import Alerts from "./views/Alerts.vue";
import Upload from "./views/Upload.vue";

const routes = [
  { path: "/", name: "dashboard", component: Dashboard },
  { path: "/estudiantes", name: "students", component: Students },
  { path: "/estudiantes/:id", name: "student", component: StudentDetail, props: true },
  { path: "/alertas", name: "alerts", component: Alerts },
  { path: "/cargar", name: "upload", component: Upload },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
