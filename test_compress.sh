IN_FILE="/BackupDrive/purchases/channels/ftv/alexis-ii/alexis-ii-00009575-07-480p.mp4"
OUT_FILE="/StorageDrive/purchases/alexis-ii-00009575-07-480p_small.mp4"
#  -hwaccel cuda
ffmpeg -i $IN_FILE -vcodec libx264 -crf 40 $OUT_FILE

