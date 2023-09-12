import axios from "axios";

const apiInstance = axios.create({
  baseURL: "http://localhost:3000",
  timeout: 1000,
  headers: { "X-Custom-Header": "foobar" },
});

const backendApi = axios.create({
  baseURL: "http://localhost:4001",
  timeout: 250000,
  headers: { "X-Custom-Header": "foobar" },
});

export { apiInstance, backendApi };
