import { createTheme } from "@mui/material";

export const theme = createTheme({
  typography: {
    fontSize: 14,
    fontFamily: ["Nunito", "sans-serif"].join(","),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: "12px",
          padding: "8px",
          fontSize: "16px",
          fontWeight: 600,
          backgroundColor: "#2970FF",
          "&:hover": {
            backgroundColor: "#2464e5",
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          fontSize: "16px",
          "& .MuiInputBase-root.Mui-focused .MuiInputBase-input::placeholder": {
            color: "#d4d4d4",
            opacity: 1,
          },
          "& .MuiInputBase-input::placeholder": {
            color: "#737373",
            opacity: 1,
          },
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderRadius: "12px",
            },
            "&.Mui-focused fieldset": {
              borderColor: "#2970FF",
              borderWidth: "2px",
            },
            "&.Mui-error fieldset": {
              borderColor: "#DC2626",
              borderWidth: "2px",
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: "16px",
        },
      },
    },
  },
});