FOLDER=/BackupDrive/purchases/tmp/test/

ffmpeg -hwaccel cuda -i $FOLDER/isla_summer_test.mp4 -vcodec libx265 -crf 30 $FOLDER/test_out2.mp4

