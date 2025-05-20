import {
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  Chip,
  CircularProgress,
  Grid,
  InputAdornment,
  Link,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Gamepad2, Laptop, SearchIcon } from "lucide-react";
import { useCallback, useState } from "react";
import axiosClient from "./libs/axiosClient";
import type { GameActionProps, GameProps, GameResponseProps } from "./types/game";
import { getColorForString } from "./types/colors";
import GameModal from "./components/game-modal";
import axios from "axios";
import toast from "react-hot-toast";

const App = () => {
  const [text, setText] = useState<string>("");
  const [games, setGames] = useState<GameProps[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [action, setAction] = useState<GameActionProps | null>();

  const onSubmit = useCallback(async () => {
    try {
      setLoading(true);
      const {
        data: { games },
      } = await axiosClient.post<GameResponseProps>("/search", {
        text: text,
      });
      setGames(games);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const { response } = error;
        toast.error(response?.data.detail);
      }
      console.log("Error: ", error);
    } finally {
      setLoading(false);
    }
  }, [text]);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <Stack
        sx={{
          paddingY: 2,
          width: "50vw",
          alignItems: "center",
        }}
      >
        <Box
          sx={{
            display: "flex",
            textAlign: "center",
            alignItems: "center",
            gap: 2,
            marginBottom: 2,
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              gap: 1,
              alignItems: "center",
            }}
          >
            <Gamepad2 size={32} />
            <Typography
              sx={{
                fontSize: 24,
                fontWeight: 600,
              }}
            >
              Game Recommendation System
            </Typography>
          </Box>
        </Box>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            width: "100%",
          }}
        >
          <TextField
            disabled={loading}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Let's us know what games you want to search"
            fullWidth
            sx={{
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderTopRightRadius: 0,
                  borderBottomRightRadius: 0,
                },
              },
            }}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              },
            }}
          />
          <Button
            type="submit"
            onClick={onSubmit}
            variant="contained"
            disabled={loading}
            sx={{
              borderTopLeftRadius: 0,
              borderBottomLeftRadius: 0,
              width: "20%",
            }}
          >
            {loading ? (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  gap: 1,
                  alignItems: "center",
                }}
              >
                <CircularProgress size={25} />
                <label>Loading...</label>
              </Box>
            ) : (
              "Search games"
            )}
          </Button>
        </Box>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            gap: 1,
            marginTop: 2,
          }}
        >
          <Typography fontWeight={600}>For example:</Typography>
          <Typography
            sx={{
              fontStyle: "italic",
            }}
          >
            I want to play a single-player racing game with high end graphics that from support French
          </Typography>
        </Box>
      </Stack>
      <Grid
        container
        spacing={4}
        sx={{
          paddingX: 8,
          marginTop: 2,
          paddingBottom: 4,
        }}
      >
        {games.map((game) => (
          <Grid size={3} key={game.app_id}>
            <Card
              sx={{
                height: "100%",
                cursor: "pointer",
                "&:hover": {
                  backgroundColor: "#f5f5f5",
                  transform: "scale(1.05)",
                  transition: "transform 0.3s ease-in-out",
                },
              }}
              onClick={() => {
                setAction({
                  type: "game-detail",
                  payload: game,
                });
              }}
            >
              <Box
                sx={{
                  position: "relative",
                }}
              >
                <CardMedia
                  component="img"
                  image={
                    game.header_image.includes("https")
                      ? game.header_image
                      : `https://placehold.co/400x188?text=${game.name}`
                  }
                  alt={game.name}
                />
                {!!game.website && (
                  <Link
                    sx={{
                      position: "absolute",
                      bottom: 10,
                      right: 10,
                      backgroundColor: "#2970FF",
                      color: "white",
                      "&:hover": {
                        backgroundColor: "#2464e5",
                      },
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                    href={game.website}
                    target="_blank"
                  >
                    <Laptop />
                  </Link>
                )}
              </Box>
              <CardContent
                sx={{
                  padding: 2,
                }}
              >
                <Box
                  sx={{
                    marginBottom: 1,
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 1,
                    alignItems: "center",
                  }}
                >
                  <Chip
                    label={game.developers}
                    sx={{
                      backgroundColor: getColorForString(game.developers),
                      fontWeight: 600,
                    }}
                  />
                  <Chip
                    label={game.release_date}
                    sx={{
                      fontWeight: 600,
                      backgroundColor: "#e5e5e5",
                    }}
                  />
                  <Chip
                    label={game.is_free ? "Free" : "Paid"}
                    sx={{
                      backgroundColor: game.is_free ? "#7ccf00" : "#ff6900",
                      border: 1,
                      fontWeight: 600,
                      color: "white",
                    }}
                  />
                </Box>
                <Typography
                  fontSize={20}
                  fontWeight={600}
                  sx={{
                    marginBottom: 2,
                  }}
                >
                  {game.name}
                </Typography>
                <Typography
                  sx={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: "2",
                    WebkitBoxOrient: "vertical",
                  }}
                >
                  {game.short_description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      {action && action.type === "game-detail" && (
        <GameModal action={action} open={action.type === "game-detail"} onClose={() => setAction(null)} />
      )}
    </Box>
  );
};

export default App;
