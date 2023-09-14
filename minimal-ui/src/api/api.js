import axios from "axios";

const apiInstance = axios.create({
  baseURL: "http://104.154.218.109",
  timeout: 1000,
  headers: { "X-Custom-Header": "foobar" },
});

const backendApi = axios.create({
  baseURL: "http://104.154.218.109",
  timeout: 1000,
  headers: { "X-Custom-Header": "foobar" },
});

export { apiInstance, backendApi };
