# Visualize where rebounds are recovered after missed three-point attempts.
# The prepared input contains one row per rebound and the credited rebounder's
# x/y coordinates near rim contact. Raw player-tracking files are not published.

library(readr)
library(ggplot2)
library(jpeg)

locations <- read_csv("data/rebound_locations.csv", show_col_types = FALSE)
court <- readJPEG("data/thunder_half_court.jpg")

ggplot(locations, aes(x = reb_x, y = reb_y)) +
  annotation_raster(court, xmin = -47, xmax = 47, ymin = -5, ymax = 45) +
  stat_density_2d(
    aes(fill = after_stat(density), alpha = after_stat(density)),
    geom = "raster",
    contour = FALSE
  ) +
  scale_fill_viridis_c(option = "magma", direction = -1) +
  scale_alpha(range = c(0, 0.82), guide = "none") +
  coord_fixed(xlim = c(-47, 47), ylim = c(-5, 45), expand = FALSE) +
  labs(
    x = "Court x-coordinate",
    y = "Court y-coordinate",
    fill = "Density"
  ) +
  theme_void() +
  theme(legend.position = "right")

ggsave(
  "results/figures/rebound_location_heatmap.png",
  width = 8.5,
  height = 5.7,
  dpi = 180
)
