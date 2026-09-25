import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "/api",
});

export default {
  summary: () => api.get("/summary/").then((r) => r.data),
  alerts: () => api.get("/alerts/").then((r) => r.data),
  baremo: () => api.get("/baremo/").then((r) => r.data),
  students: (params = {}) =>
    api.get("/students/", { params }).then((r) => r.data),
  student: (id) => api.get(`/students/${id}/`).then((r) => r.data),
  upload: (file, sheet) => {
    const form = new FormData();
    form.append("file", file);
    if (sheet) form.append("sheet", sheet);
    return api
      .post("/upload/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};
