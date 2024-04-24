export const fs = (score: number) => {
  return score;
  return score < 0.6 ? score + 0.3 : score;
};
