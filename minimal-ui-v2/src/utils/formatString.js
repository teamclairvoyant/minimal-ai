export function formatNodeName(name) {
  return name.toLowerCase().replace(/[\W]/g, "_");
}

export function getUuidFromPath(path) {
  const path_list = path.split("/");

  if (path_list.length > 3) {
    return path_list[2];
  }
  return path_list.pop();
}
