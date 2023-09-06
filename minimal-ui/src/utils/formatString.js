export function formatNodeName(name) {
  return name.toLowerCase().replace(/[\W]/g, "_");
}

export function getUuidFrpmPath(path) {
  return path.split("/").pop();
}
