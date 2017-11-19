#!A:\!Soft\00_DEV_LANG\Python27\python.exe
# -*- coding: utf-8 -*-

#  Photo file
#   YYYY-MM-DD HH-MM-SS_ss - Camera model
#       Example:
#               2014-09-01 06-06-15_89 - Canon EOS 7D.JPG



#exiftool  -copyright="De4m (De4m@yandex.ru)(ShotDate:2017:02:11 11:55:52)" test.thm
#
#
#
#
#
#

import os
import re
import sys
import time
import json
import argparse


def main():
    """
        Main function
    """
    
    
    # Check Python ver great 3.0
    if sys.version_info > (3, 0): 
        print ('\n',"This program don't work in Python 3.X",'\n','Press any key')
        input()
        sys.exit(0)

    new_dirs = {}
    new_files = []

    # parse arguments parametre
    parser = argparse.ArgumentParser(description='Rename photo file and move to folder')
    #parser.add_argument('-v', '--verbose' , help='verbose out info', action = 'count')
    parser.add_argument( 'path' , help='path to photo folder', action = 'store')
    #parser.add_argument('-b', '--bath', help='no make bath file',action ='store_const', const = False )
    parser.add_argument('-j', '--json', help='create JSON file with source file',action ='store_const', const = True)
    res=parser.parse_args()
    # check and prepare path
    if res.path == None:  res.path = os.getcwd()    # get folder path from active folder
    if      res.path[len(res.path)-1] == '"'    : res.path = res.path[:len(res.path)-1] # remove ["] in end string
    elif    res.path[len(res.path)-1] == '\\'   : res.path = res.path[:len(res.path)-1] # remove [\] in end string
    elif    os.path.isdir(res.path) == False    : res.path=os.path.dirname(res.path)    # if path has file name -> remove file name
    
    #print ('\nPath:'+str(res.path).decode('cp1251','ignore')   )
    #print ('\nPath:'+str(res.path))
 
    # create json data with exif
    try: 
                                                                                   # exception control
        print ('Get EXIF data for all files')
        file_json   = os.popen('exiftool -json -s -charset FileName=CP1251 -G "'+str(res.path)+'\\*.*"').read()    # read json data 
        files_exif  = json.loads(file_json)                                             # desearelised json data
    except Exception as e:
        return 1
    print ('Read exif data is complete')

    # make json file with exif if has argument '-j' or '--json'
    if res.json == True:
        print ('Create json file with EXIF')
        f=open (str(res.path)+'\EXIF.json','w')     # write file with JSON data
        f.write (file_json)
        f.close()


    # parse each file data
    item = 0
    for file_exif in files_exif :
        tmp = {}
        tmp['Item']     = item
        tmp['OK']       = True
        tmp['SrcPath']  = file_exif['File:Directory']
        tmp['SrcFile']  = file_exif['File:FileName']

        Create_DateTime = ''
        CameraModel = ''
        ImageSize = ''
        FrameRate = ''
        Suffix = ''
        item=item+1

        print (item)
        print ('  File Name  : '+str(file_exif['File:FileName'].encode('cp866','ignore')))
        print ('  Full EXIF  : '+str(file_exif).encode('cp866','ignore') )

        # continue if mime type is not unknown
        try:
            if str(file_exif['ExifTool:Error'])=='Unknown file type':
                print ('  MIME Type  : '+str(file_exif['ExifTool:Error']))
                continue
        except Exception as e:
            pass

        # parse EXIF data
        try: 
                   
            print ('  MIME Type  : '+str(file_exif['File:MIMEType']))
            if        file_exif['File:FileType'] == 'THM':
                        # Date and time
                        try:
                            Create_DateTime = file_exif['File:FileCreateDate']
                        except Exception as e:
                            Create_DateTime = ''
                        # Camera model
                        CameraModel     = ''
                        # Image Size
                        try:
                            ImageSize   = str(file_exif['Composite:ImageSize'])
                        except Exception as e:
                            ImageSize   =''
                        FrameRate   = ''
                        Suffix          = ImageSize +' ' + FrameRate
                                          
            elif      file_exif['File:MIMEType'] == 'image/x-canon-cr2'   :
                        # camera model
                        try:
                            CameraModel = file_exif['EXIF:Model']   # camera model
                        except Exception as e:
                            CameraModel = ''
                        # Date and time
                        try:
                            Create_DateTime = file_exif['Composite:SubSecDateTimeOriginal']
                        except Exception as e:
                            try:
                                Create_DateTime = file_exif['EXIF:DateTimeOriginal']
                            except Exception as e:
                                Create_DateTime = ''
                        # Suffix
                        Suffix = CameraModel

            # Apple
                       
            elif       get_vendor(file_exif) == 'Apple'            :   
              print ('  Vendor     : Apple')                          
              if file_exif['File:MIMEType'] == 'image/jpeg' :
                if       file_exif['EXIF:LensModel'][0:9] == 'iPhone 5s'  :
                  CameraModel     = file_exif['EXIF:LensModel'][0:9]
                  Create_DateTime = file_exif['File:FileModifyDate'][:19]
                  ImageSize       = str(file_exif['EXIF:ExifImageWidth']) + 'x' + str(file_exif['EXIF:ExifImageHeight'])
                  FrameRate       = ''
                  Suffix          = CameraModel 
                if       file_exif['EXIF:LensModel'][0:9] == 'iPhone SE'  :
                  CameraModel     = file_exif['EXIF:LensModel'][0:9]
                  Create_DateTime = file_exif['Composite:SubSecDateTimeOriginal']
                  ImageSize       = str(file_exif['EXIF:ExifImageWidth']) + 'x' + str(file_exif['EXIF:ExifImageHeight'])
                  FrameRate       = ''
                  Suffix          = CameraModel 
                pass  
              if file_exif['File:MIMEType'] == 'video/quicktime':   
                 try:
                   CameraModel  = file_exif['QuickTime:Model']  
                 except Exception as e:
                   CameraModel  = ''  
            
                 try:
                   Create_DateTime  = file_exif['QuickTime:CreateDate']
                 except Exception as e:
                   Create_DateTime  = ''  
                
                 try:
                   ImageSize  = file_exif['Composite:ImageSize']  
                 except Exception as e:
                   ImageSize  = '' 
                
                 try:
                  FrameRate  = str(file_exif['QuickTime:VideoFrameRate'])  
                 except Exception as e:
                  FrameRate       = '' 
                
                 Suffix = ImageSize + ' ' + FrameRate + ' - ' + CameraModel                     
                             
               
                                
                   
            elif get_vendor(file_exif) == 'Canon EOS 7D'            : 
              if file_exif['File:MIMEType'] == 'image/jpeg' :
                 try:
                   CameraModel  = file_exif['EXIF:Model']  
                 except Exception as e:
                   CameraModel  = ''  
            
                 try:
                   Create_DateTime  = file_exif['Composite:SubSecDateTimeOriginal']
                 except Exception as e:
                   Create_DateTime  = ''  
                
                 try:
                   ImageSize  = file_exif['Composite:ImageSize']  
                 except Exception as e:
                   ImageSize  = '' 
                
                 FrameRate       = '' 
                
                 Suffix          = CameraModel 
                
            
            
            
            
              if file_exif['File:MIMEType'] == 'video/quicktime':
               try:
                 CameraModel  = file_exif['QuickTime:Model']  
               except Exception as e:
                 CameraModel  = '' 
                
               try:
                 Create_DateTime  = file_exif['QuickTime:CreateDate']  
               except Exception as e:
                 Create_DateTime  = ''
               
               try:
                 ImageSize  = file_exif['Composite:ImageSize']  
               except Exception as e:
                 ImageSize  = ''
                     
               try:
                 FrameRate  = str(file_exif['QuickTime:VideoFrameRate'])  
               except Exception as e:
                 FrameRate       = '' 
                
               Suffix = ImageSize + ' ' + FrameRate + ' - ' + CameraModel                     
                
                
            # Samsun GalagyS3 (GT-I9300)
            #       Photo                       Video
            #       EXIF:Model                  XMP:CameraModel
            #       EXIF:DateTimeOriginal       QuickTime:CreateDate
            #       Composite:ImageSize         Composite:ImageSize 
            #       -----                       QuickTime:VideoFrameRate
            elif get_vendor(file_exif) == 'GT-I9300'            :         
              if file_exif['File:MIMEType'] == 'image/jpeg':
                try:
                  CameraModel  = file_exif['EXIF:Model']  
                except Exception as e:
                  CameraModel  = ''  
            
                try:
                  Create_DateTime  = file_exif['EXIF:DateTimeOriginal']  
                except Exception as e:
                  Create_DateTime  = ''  
                
                try:
                  ImageSize  = file_exif['Composite:ImageSize']  
                except Exception as e:
                  ImageSize  = '' 
                
                FrameRate       = '' 
                
                Suffix          = CameraModel 
                print ('-----------'+Suffix )
                
                                             
              if file_exif['File:MIMEType'] == 'video/mp4':  
                CameraModel  = file_exif['XMP:CameraModel']
                try:
                  CameraModel  = file_exif['XMP:CameraModel']  
                except Exception as e:
                  CameraModel  = '' 
            
                try:
                  Create_DateTime  = file_exif['QuickTime:CreateDate']  
                except Exception as e:
                  Create_DateTime  = ''
                
                try:
                  ImageSize  = file_exif['Composite:ImageSize']  
                except Exception as e:
                  ImageSize  = ''
                      
                try:
                  FrameRate  = str(file_exif['QuickTime:VideoFrameRate'])  
                except Exception as e:
                  FrameRate       = '' 
                
                Suffix = ImageSize + ' ' + FrameRate + ' - ' + CameraModel 
                print ('-----------'+Suffix )
            
         
                
             
            elif    file_exif['File:MIMEType'] == 'image/jpeg'          :
                        # camera model
                        try:
                            CameraModel = file_exif['EXIF:Model']
                        except Exception as e:
                            CameraModel = ''
                        # Date and time
                        try:
                            Create_DateTime = file_exif['Composite:SubSecDateTimeOriginal']
                        except Exception as e:
                            try:
                                Create_DateTime = file_exif['EXIF:DateTimeOriginal']
                            except Exception as e:
                                Create_DateTime = ''

                        # Suffix
                        Suffix = CameraModel

            elif    file_exif['File:MIMEType'] == 'image/x-nikon-nef'  :
                        # camera model
                        try:
                            CameraModel = file_exif['EXIF:Model']
                        except Exception as e:
                            CameraModel = ''
                        # Date and time
                        try:
                            Create_DateTime = file_exif['Composite:SubSecDateTimeOriginal']
                        except Exception as e:
                            try:
                                Create_DateTime = file_exif['EXIF:DateTimeOriginal']
                            except Exception as e:
                                Create_DateTime = ''
                        # Suffix
                        Suffix = CameraModel

            elif    file_exif['File:MIMEType'] == 'video/mp4'           :
                        Create_DateTime = file_exif['QuickTime:CreateDate']
                        CameraModel     = ''
                        # GoPro HD5
                        try:
                            TMP_CameraModel = file_exif['QuickTime:FirmwareVersion'][:3]
                            if TMP_CameraModel == 'HD5':
                              CameraModel = 'HERO5 Black'  
                        except Exception as e:
                            CameraModel = ''
                            
                        
                        ImageSize       = str(file_exif['QuickTime:ImageWidth']) + 'x' + str(file_exif['QuickTime:ImageHeight'])
                        FrameRate       = str(file_exif['QuickTime:VideoFrameRate'])
                        Suffix          = ImageSize +' ' + FrameRate  + ' - ' + CameraModel


            elif    file_exif['File:MIMEType'] == 'video/quicktime'     : 
                        Create_DateTime = file_exif['QuickTime:CreateDate']
                        CameraModel     = ''
                        ImageSize       = str(file_exif['QuickTime:ImageWidth']) + 'x' + str(file_exif['QuickTime:ImageHeight'])
                        FrameRate       = str(file_exif['QuickTime:VideoFrameRate'])
                        Suffix          = ImageSize +' ' + FrameRate
            
            
         
            elif    file_exif['File:MIMEType'] == 'video/x-msvideo'     :
                        # Date and time
                        try:
                            Create_DateTime = file_exif['RIFF:DateTimeOriginal']
                        except Exception as e:
                            Create_DateTime = ''
                        # Camera model
                        CameraModel     = ''
                        # Image Size
                        try:
                            ImageSize   = str(file_exif['RIFF:ImageWidth']) + 'x' + str(file_exif['RIFF:ImageHeight'])
                        except Exception as e:
                            ImageSize   =''
                        # Frame rate
                        try:
                            FrameRate   = str(file_exif['RIFF:VideoFrameRate'])
                        except Exception as e:
                            FrameRate   = ''
                        Suffix          = ImageSize +' ' + FrameRate

            # convert date from 2014:09:01 12:06:06.21 to 2014-09-01 12-06-06_21
            Create_DateTime = re.sub(':','-',Create_DateTime)
            Create_DateTime = re.sub('\.','_',Create_DateTime)

            # prepare destination path and file
            tmp['DstFile'] = Create_DateTime + ' - ' + Suffix+'.'+str(file_exif['File:FileTypeExtension']).upper()
            tmp['DstPath'] = tmp['SrcPath']+'\\'+Create_DateTime[0:10]


            print ('  CamModel   : '+str(CameraModel))
            print ('  CreateData : '+str(Create_DateTime))
            print ('  ImageSize  : '+str(ImageSize))
            print ('  FrameRate  : '+str(FrameRate))
            print ('  DstFileName: '+str (tmp['DstFile']))
            #print ('  DstPathName: '+str (tmp['DstPath']).decode('cp1251','ignore') )




            if ( Create_DateTime == '' or Suffix == ''):
                tmp['OK'] = False
                continue

            # need create new folder
            new_dirs[str(Create_DateTime[0:10])] = ''
            new_files.append(tmp)

            pass
        except Exception as e:
            tmp['OK'] = False
            print ('Error'+str(e))
            pass

    print ('\n----------------------------------------------------------------------------')
    print (': {0:30} -> {1:30} '.format(*['In','Out']))     
    print ('----------------------------------------------------------------------------')  
    tmp_i = 0
    for tmp in new_files:
      for tmp1  in new_files: 
        if tmp['Item'] == tmp1['Item']:continue
        if tmp['SrcFile'][-3:] == 'THM':
           if tmp['SrcFile'][:-3] == tmp1['SrcFile'][:-3]:  
              tmp['DstFile'] = str(tmp1['DstFile'])[0:-3] + str('THM')
              tmp['DstPath'] = tmp1['DstPath']   
        if tmp['DstFile']  == tmp1['DstFile']:   
           tmp_i = tmp_i + 1 
           tmp1['DstFile'] = tmp1['DstFile'][:-4]+'_'+str(tmp_i)+tmp1['DstFile'][-4:]     
       
      #if tmp['SrcFile'][-3:] == 'THM':
      #  for tmp1 in new_files: 
      #    if tmp['Item'] == tmp1['Item']:continue
      #    if tmp['SrcFile'][:-3] == tmp1['SrcFile'][:-3]:  
      #      tmp['DstFile'] = str(tmp1['DstFile'])[0:-3] + str('THM')
      #      tmp['DstPath'] = tmp1['DstPath']    
            
      print (': {0:30} -> {1:30} '.format(*[tmp['SrcFile'],tmp['DstFile']]))  
     

    # create Bath file
    f=open (res.path+'\\Rename.bat','w')
    for new_dir in new_dirs:                        # create folder
        f.write ('mkdir '+str (new_dir)+'\n')
    for tmp in new_files:
        # Only for Python 2.x
        f.write ('move /-Y  "' +    str(tmp['SrcPath'].encode('cp866','ignore'))  + '\\' +
                                    str(tmp['SrcFile'].encode('cp866','ignore'))  + '" "' +
                                    str(tmp['DstPath'].encode('cp866','ignore'))  + '\\' +
                                    str(tmp['DstFile'].encode('cp866','ignore'))  + '"\n')

    f.close



    #ctime = time.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
    #subsecond = tags['EXIF SubSecTimeOriginal']
    #print ('\n\n\n\n'+str (ctime))



    pass   
    
def get_vendor(_file_exif):
    vendor = '' 
    
    # Apple
    try:
      vendor = _file_exif['EXIF:LensMake']  
      return vendor
    except Exception as e:
      vendor = ''
                  
    try:
      vendor = _file_exif['QuickTime:HandlerVendorID']  
      return vendor
    except Exception as e:
      vendor = ''      

      
      
    # Canon EOS; (video)
    try:
      vendor = _file_exif['QuickTime:Model'] 
      return vendor
    except Exception as e:
      vendor = '' 
      
    # GalaxyS3; BlackCam; RedCam (video)
    try:
      vendor = _file_exif['XMP:CameraModel']     
      return vendor
    except Exception as e:
      vendor = ''  
                         
        
    # Canon EOS; GalaxyS3 (Photo)
    try:
      vendor = _file_exif['EXIF:Model']  
      return vendor
    except Exception as e:
      vendor = '' 


    
if __name__ == '__main__':
    main()

"""
"""
