#!/usr/bin/env python
# encoding: utf-8
'''
src.Asc -- shortdesc

src.Asc is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2019 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import argparse;
from exif._constants import Orientation

__all__ = []
__version__ = 0.1
__date__ = '2019-12-27'
__updated__ = '2019-12-27'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        #parser = argparse.OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser = argparse.ArgumentParser()
        parser.add_argument("infile", help="set input folder", metavar="INPUTFOLDER")
        parser.add_argument("apikey", help="apikey for bing maps, see https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key", metavar="APIKEY")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level", default = 0)
        parser.add_argument("-o", "--out", dest="outfile", help="set output path", metavar="FILE", default = 'result.jpg')
        parser.add_argument("-n", "--numcols", dest="numcols", help="number of columns", type=int, default=4)
        parser.add_argument("-s", "--size", dest="size", help="size, default 256", type=int, default = 256)
        parser.add_argument("-d", "--dimension", dest="dimension", help="amount of columns the map uses", type=int,default = 2)
        parser.add_argument("-z", "--zoom", dest="zoom", help="zoom of map (0-22), more = more zoomed, 0 = best fit", type=int,default = 0)
        parser.add_argument("-b", "--begin", dest="begin", help="first character of label", type=int,default = 5)
        parser.add_argument("-a", "--amount", dest="amount", help="amount of characters for label", choices=[1, 2, 3],type=int,default = 3)
        
        #requiredNamed.add_argument("-k", "--key", dest="apikey", help="apikey for bing maps, see https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key")
        

        # set defaults
        #parser.set_defaults(outfile="./out.txt", infile="./in.txt")
        
        # process options
        (args) = parser.parse_args(argv)
        #args.apikey= args.key;
        if args.size > 512 or args.size < 64:
            parser.error('size invalid (64-512)');
            
            
            
        if args.verbose > 0:
            print("verbosity level = %d" % args.verbose)
        if args.infile:
            print("folder = %s" % args.infile)
        if args.outfile:
            print("outfile = %s" % args.outfile)

        # MAIN BODY #
        from exif import Image;
        pos = [];
        for file in os.listdir( args.infile):
            if(file.lower().endswith(".jpg")):
                if args.verbose > 0:
                    print(os.path.join(args.infile,file));
                with open(os.path.join(args.infile,file),'rb') as image_file:
                    my_image = Image(image_file);
                    #print(dir(my_image));
                    #print(my_image.orientation);
                    try:
                        #print('x'+str(my_image.gps_latitude));
                        #print('y'+str(my_image.gps_longitude));
                        try:
                            pos.append((file,my_image.gps_longitude,my_image.gps_latitude,os.path.join(args.infile,file),my_image.orientation));
                        except:
                            pos.append((file,my_image.gps_longitude,my_image.gps_latitude,os.path.join(args.infile,file),1));
                        
                    except AttributeError as a:
                        if args.verbose > 0:
                            print('\tWARNING: ignored - no geopos or orientation found');
                        pass;
        mapsize = (args.size*args.dimension);
        url = "https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels?mapSize="+str(mapsize)+","+str(mapsize)+"&zoomLevel="+str(args.zoom)+"&key="+args.apikey
        from PIL import Image, ImageDraw, ImageFont
        size = (args.size, args.size,)
        perrow=args.numcols+args.dimension;
        
        fnt = ImageFont.truetype('arialbd.ttf', 15)
        
        slots = len(pos)+args.dimension*args.dimension;
        hei = max(args.dimension,slots // (args.numcols)) 
        #print(hei);
        img = Image.new('RGB', (args.size*perrow, args.size*hei), color = 'white');
        dr = ImageDraw.Draw(img)
        
        
        i = args.dimension;
        j = 0;
        num = 0;
        for token in pos:
            #API unterstützt nur 18 Marker
            if num == 18:
                if args.verbose > 0:
                    print('INFO: more that 18 pictures, only 18 pictures are supported')
                break;
            num+=1;
            timg = Image.open(token[3]);
            if(token[4] == Orientation.RIGHT_TOP):
                timg = timg.rotate(270, Image.NEAREST, expand = 1)
            elif(token[4] == Orientation.RIGHT_BOTTOM):
                timg = timg.rotate(90, Image.NEAREST, expand = 1)
            elif(token[4] == Orientation.LEFT_BOTTOM):
                timg = timg.rotate(180, Image.NEAREST, expand = 1)
            timg.thumbnail(size);
            label = token[0][args.begin:(args.begin+args.amount)];
            if label == '':
                label = "{:03d}".format(1);
            
            #timg.show();
            img.paste(timg,(i*args.size,j*args.size));
            
            dr.rectangle(((i*args.size,j*args.size),(i*args.size+35,j*args.size+20)), fill='black');
            dr.text((i*args.size+2,j*args.size+2), label, font=fnt,fill=(255,255,255))
            
            #dr.text((i*256+10,(1+j)*256-20), label, font=fnt,fill=(255,255,255))
            i = i+1;
            if(i == perrow):
                j = j+1;
                i = 0;
                if(j < args.dimension):
                    i = args.dimension;
            #imgs.append(PIL.Image.open(token[3]));
            
            
            yy = token[1][0] + token[1][1]/60 + token[1][2]/3600;
            xx = token[2][0] + token[2][1]/60 + token[2][2]/3600;
            url = url+'&pushpin='+str(xx)+","+str(yy)+';1;'+str(label);
            
            #img.save("C:/TEMP/out.jpg", "JPEG", quality=80, optimize=True, progressive=True)
        print('mapUrl = '+url)
        import urllib.request;
        urllib.request.urlretrieve(url, "map.jpg");
        im = Image.open("map.jpg");
        img.paste(im,(0,0));
        img.save(args.outfile, "JPEG", quality=80, optimize=True, progressive=True)
        if args.verbose > 0:
            Image.open(args.outfile).show();
        

    except KeyError as e:
        print(e);
        import traceback;
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    if DEBUG:
        pass;
        #main(sys.argv);
        
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'src.Asc_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())