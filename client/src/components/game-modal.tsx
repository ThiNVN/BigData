import { Box, Chip, Dialog, DialogTitle, Grid, IconButton, Link } from "@mui/material";
import type { GameActionProps } from "../types/game";
import { useMemo } from "react";
import { Laptop, X } from "lucide-react";
import { convertToArray } from "../utils/char";

interface GameModalProps {
  action: GameActionProps;
  open: boolean;
  onClose: () => void;
}

const GameModal = ({ action, open, onClose }: GameModalProps) => {
  const game = useMemo(() => action.payload, [action]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <Box
        sx={{
          position: "relative",
        }}
      >
        <img src={game.header_image} alt={game.name} style={{ width: "100%" }} />
        <IconButton
          onClick={onClose}
          sx={{
            position: "absolute",
            top: 8,
            right: 8,
            backgroundColor: "white",
            padding: 1,
            color: "black",
            "&:hover": {
              backgroundColor: "#f5f5f5",
            },
          }}
        >
          <X size={18} />
        </IconButton>
      </Box>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          paddingRight: "2rem",
        }}
      >
        <DialogTitle
          variant="h5"
          fontWeight={600}
          sx={{
            maxWidth: "60%",
          }}
        >
          {game.name}
        </DialogTitle>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, justifyContent: "center" }}>
          {!!game.website && (
            <Link href={game.website} target="_blank">
              <Laptop size={24} />
            </Link>
          )}
          <Chip
            label={`Total recommendations: ${game.recommendations_total}`}
            sx={{
              fontWeight: 600,
            }}
          />
        </Box>
      </Box>
      <Grid container spacing={1} paddingX={3} paddingBottom={3}>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          1. Developers:
        </Grid>
        <Grid size={9}>{game.developers}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          2. Publishers:
        </Grid>
        <Grid size={9}>{game.publishers}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          3. Description:
        </Grid>
        <Grid size={9}>{game.short_description}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          4. Release date:
        </Grid>
        <Grid size={9}>{game.release_date}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          5. Categories:
        </Grid>
        <Grid size={9}>{convertToArray(game.categories).join(", ")}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          6. Genres:
        </Grid>
        <Grid size={9}>{convertToArray(game.genres).join(", ")}</Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          7. Price:
        </Grid>
        <Grid size={9}>
          {game.price_final} {game.price_currency}
        </Grid>
        <Grid
          size={3}
          sx={{
            fontWeight: 600,
          }}
        >
          8. Languages:
        </Grid>
        <Grid size={9}>{game.supported_languages.join(", ")}</Grid>
      </Grid>
    </Dialog>
  );
};

export default GameModal;
