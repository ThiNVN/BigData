export function convertToArray(str: string) {
  return str
    .replace("[", "")
    .replace("]", "")
    .split(",")
    .map((temp) => temp.trim().slice(1, -1));
}