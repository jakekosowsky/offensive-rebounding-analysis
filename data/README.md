# Data notes

The play-by-play analysis expects `2019-20_pbp.csv` in this directory. The directional visualization uses `testing_data_pbp.csv` and `testing_data_loc.csv`, a separate tracking sample containing player coordinates at shot release and near rim contact.

Because this sample does not include a credited rebounder identifier, the visualization uses the location of the player nearest the rim at rim contact as a transparent rebound-position proxy. The raw tracking files are not published here; the aggregate visualization and its preparation code are included.
