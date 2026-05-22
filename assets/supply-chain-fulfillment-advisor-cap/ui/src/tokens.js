export const COLORS = {
  bgNavy:      '#0d1b2a',
  bgCard:      '#1a2b3c',
  bgCardHover: '#1e3347',
  border:      '#2a3f55',
  textPrimary: '#e8f4f8',
  textMuted:   '#7a9bb5',
  accentRed:   '#e63946',
  accentGreen: '#2ec4b6',
  accentAmber: '#f4a261',
  accentBlue:  '#4fc3f7',
};

export const STATUS_COLORS = {
  ON_TRACK:             COLORS.accentGreen,
  AT_RISK:              COLORS.accentAmber,
  ESCALATION_REQUIRED:  COLORS.accentRed,
  healthy:              COLORS.accentGreen,
  warning:              COLORS.accentAmber,
  critical:             COLORS.accentRed,
  neutral:              COLORS.accentBlue,
  supplier:             COLORS.accentBlue,
  plant:                COLORS.accentGreen,
  dc:                   COLORS.accentAmber,
  customer:             COLORS.textPrimary,
};
