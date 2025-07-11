# Torrent handling module
#
# Problem 1:
# Moving the files may fail/corrupt if torrent is still seeding.
# This can be mitigated by checking if the torrent is still seeding before moving it, and then stopping the seed or returning at a later run?
# Problem 2:
# Lingering torrents will cause a new directory to be created with the same name.
