from PIL import Image,ImageEnhance,ImageFilter
import sys, urllib2, os, errno, shutil, glob
from StringIO import StringIO
from svm import *
from svmutil import *
svm_model.predict = lambda self, x: svm_predict([0], [x], self)[0][0]

WIDTH=18
HEIGHT=18
url = 'http://www.vipin.us/imagecode.jsp?v=login'
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
#url = 'https://dynamic.12306.cn/otsweb/passCodeAction.do?rand=sjrand'

def createdir(filelist):
    for file in filelist:
    	for s in list(os.path.splitext(file)[0]):
    	   if(not os.path.exists(s)):
    	   		os.mkdir(s)

def downUrl(url):
    f = urllib2.urlopen(url)
    try:
        data =  f.read()
    finally: 
        f.close()
    return data

def bw(file):
	im = Image.open(file)
	im2 = Image.new("P",im.size, 255)
	for x in range(im.size[0]):
	  for y in range(im.size[1]):
	    r,g,b = im.getpixel((x,y))
	    if (r >=150 and g >= 150 and b >= 150):
	    	im2.putpixel((x,y), 255)
	    else:
	    	im2.putpixel((x,y), 0)
	return im2    	

def seg(im2):	
	inletter = False
	foundletter=False
	start = 0
	end = 0

	letters = []
	for x in range(im2.size[0]): # slice across
	  for y in range(im2.size[1]): # slice down
	    pix = im2.getpixel((x,y))	    
	    if pix != 255:
	      inletter = True
	  
	  if foundletter == False and inletter == True:
	    foundletter = True
	    start = x

	  width = x - start
	  if(width>17 and inletter == True):	    		    	
	    	foundletter = False
	    	end = x
    		letters.append((start,end))
    		start = end
	  else:  
		    if foundletter == True and inletter == False:
		    	foundletter = False
		    	end = x
		    	if(width > 1 and width <=17):		    		
		    		letters.append((start,end))
		    		inletter=False	  
	  inletter=False
	
	imgdata = [];
	for letter in letters:
		im3 = im2.crop(( letter[0] , 0, letter[1],im2.size[1] ))
		miny=100000
		maxy=0
		for i in range(im3.size[0]):
		    for j in range(im3.size[1]):
		        if im3.getpixel((i,j)) == 0:
		            if j<miny:
		                miny=j
		            if j>maxy:
		                maxy=j        

		im4 = im3.crop((0, miny, im3.size[0], maxy+1))		
		sizei = maxy-miny+1		

		im = Image.new('P', (WIDTH, HEIGHT), 255)
		im.paste(im4, ((WIDTH-im3.size[0])/2, (HEIGHT - sizei)/2))		
		imgdata.append(list(im.getdata()))

	return imgdata

def makeTrainSet(files):
	x=[]
	y=[]
	
	for f in files:	 	
	 	im2 = bw(f)
	 	[chars, imgdata] = [list(os.path.splitext(os.path.basename(f))[0]), seg(im2)]
		#m = hashlib.md5()
		#m.update("%s%s"%(time.time(),count))	  
	  	#im3.save("./%s/%s.gif"%(chars[count] , m.hexdigest()))

	 	for ch in chars:	 		
	 		x.append(ord(ch))
	 		y.append(map(lambda x: 1 if x==255 else 0, imgdata.pop(0)))

	prob = svm_problem(x, y)       		
	param = svm_parameter()
	param.kernel_type = LINEAR
	param.C = 1
	param.nr_fold=10
	param.cross_validation=True

	return svm_train(prob, param)

def downExamples(num):
	for i in range(500,1000):
		u = downUrl(url)
		localFile = open('e/%s.jpg' % i, 'w')
		print i
		localFile.write(u)
		localFile.close()		

def predict(file, modelName):	
	model = svm_load_model(__location__ + "/models/" + modelName)
	im2 = bw(file)
	im2.show()
	imgdata = seg(im2)
	answer=[]
	for img in imgdata:
		p_label, p_acc, p_val = svm_predict([0], [map(lambda x: 1 if x==255 else 0,img)], model, '-q')
		char = chr(int(p_label[0]))
		#ind = model.predict(map(lambda x: 1 if x==255 else 0,im3.getdata()))
		answer.append(char)		
	return ''.join(answer)

if __name__ == '__main__':
	#downExamples(500)
	#files = glob.glob('examples/*.jpg')
	#model = makeTrainSet(files)
	#svm_save_model('vipin.m', model)	
	for i in range(5):
		print str(i) + predict(StringIO(downUrl(url)))
