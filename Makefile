
videosite:
	python make_vidsite.py

copy_imgs:
	rsync -am --include='*.jpeg' --include='*.jpg' --include='*.png' --include='*/' --exclude='*' /AddStorage/uncompressed/ /AddStorage/compressed_unsorted/

copy_img_vids:
	rsync -am --include='*.mp4' --include='*/' --exclude='*' /AddStorage/newly_compressed_images/ /StorageDrive/purchases/images/

copy_vids:
	rsync -am --include='*.mp4' --include='*/' --exclude='*' /AddStorage/compressed_unsorted/ /StorageDrive/purchases

copy_vids_rm_old:
	rsync -am --remove-source-files --include='*.mp4' --include='*.png' --include='*.jpeg' --include='*.jpg' --include='*.webm' --include='*/' --exclude='*' /AddStorage/compressed_unsorted/ /StorageDrive/purchases
