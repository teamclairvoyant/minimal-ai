import axios from "axios";

const backendApi = axios.create({
  baseURL: "http://127.0.0.1:4001/api/v1",
  timeout: 5000,
  headers: { "X-Custom-Header": "foobar" },
});

export { backendApi };
