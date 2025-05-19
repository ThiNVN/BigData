import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { CssBaseline, StyledEngineProvider, ThemeProvider } from "@mui/material";
import { theme } from "./themes/theme";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <App />
        <CssBaseline />
      </ThemeProvider>
    </StyledEngineProvider>
  </StrictMode>
);
