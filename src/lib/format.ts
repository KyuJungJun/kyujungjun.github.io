const M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const monthYear = (d: Date) => `${M[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
