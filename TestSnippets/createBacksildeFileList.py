import os

#PicturePath='/links/Photos/Converted/1920/2015/201508_Sommer'
PicturePath='/links/Photos/Converted/1920/2016/201609_Sommer'
Pictures = os.listdir(path=PicturePath) 
#print(Pictures)
out = '"['
for idx,pict in enumerate(Pictures):
    print(pict)
    if idx == 0:
        out =out + "'" + str(os.path.join( PicturePath, pict)) + "'"
    else:
        out =out + ",'" + str(os.path.join( PicturePath, pict)) + "'"
out = out+']"'
#print(out)
command='dconf write /org/gnome/shell/extensions/backslide/image-list ' + out
print(command)
os.system(command)
    