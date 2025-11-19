import defaultTheme from "tailwindcss/defaultTheme";
import colors from "tailwindcss/colors";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    // ⭐ Restore EVERYTHING Tailwind removed in v4
    colors: {
      ...colors, // full color palette
    },

    fontFamily: {
      sans: ["Inter", "Segoe UI", "Roboto", "Helvetica", "Arial", "sans-serif"],
    },

    // ⭐ Restore missing spacing, borders, radii, shadows, sizes
    // Tailwind v4 keeps these but we extend them for safety
    extend: {
      // full default spacing scale
      spacing: {
        ...defaultTheme.spacing,
      },

      borderRadius: {
        ...defaultTheme.borderRadius,
      },

      boxShadow: {
        ...defaultTheme.boxShadow,
      },

      maxWidth: {
        ...defaultTheme.maxWidth,
      },

      screens: {
        ...defaultTheme.screens,
      },

      zIndex: {
        ...defaultTheme.zIndex,
      },

      opacity: {
        ...defaultTheme.opacity,
      },

      backgroundColor: {
        ...colors,
      },

      textColor: {
        ...colors,
      },

      borderColor: {
        ...colors,
      },

      ringColor: {
        ...colors,
      },

      ringOffsetColor: {
        ...colors,
      },

      gradientColorStops: {
        ...colors,
      },

      divideColor: {
        ...colors,
      },
    },
  },

  plugins: [],
};
