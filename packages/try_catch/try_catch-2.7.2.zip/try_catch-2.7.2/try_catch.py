try:
      data=open('sketch.txt')

      for each_line in data:
          try:              
            (role,line_spoken)=each_line.split(':',1)
            print(role)     
            print('said:')  
            print(line_spoken)
          except ValueError:
               pass
      
      data.close()  
except IOError: 
    print('File Error:')

    
