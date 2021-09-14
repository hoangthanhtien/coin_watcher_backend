# import os
#os.system('termgraph ./ex4.dat --color {yellow,green}')
os.system("t.ermgraph ./ex4.dat --color yellow blue --title \"Biểu đồ giá crypto hiện tại\"")
#os.system('pwd')
f = open("test_file.dat",'w')
f.write("Header\n")
f.write("Body\n")
f.write("footer\n")
f.close()
