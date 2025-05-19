export const randomColors = [
  "#EF4444", // red-500
  "#93C5FD", // blue-300
  "#16A34A", // green-600
  "#FACD15", // yellow-400
  "#4338CA", // indigo-700
  "#FBCFE8", // pink-200
  "#A855F7", // purple-500
  "#6EE7B7", // emerald-300
  "#0891B2", // cyan-600
  "#BEF264", // lime-400
  "#14B8A6", // teal-500
  "#FDBA74", // orange-300
  "#E11D48", // rose-600
  "#60A5FA", // sky-400
  "#C026D3", // fuchsia-700
  "#E9D5FF", // violet-200
  "#F59E0B", // amber-500
];

export function getColorForString(str: string): string {
  const index = Array.from(str).reduce((acc, char) => acc + char.charCodeAt(0), 0) % randomColors.length;
  return randomColors[index];
}