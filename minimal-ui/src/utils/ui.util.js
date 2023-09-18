export const getTitleForSidebar = (type) => {
    const title = {
        "input": "Source",
        "default": "Transformation",
        "output": "Target"
    }
    return title[type] || "";
}