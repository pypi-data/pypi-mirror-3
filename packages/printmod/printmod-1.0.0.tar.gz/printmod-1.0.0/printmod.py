""" This is my first python module, Trinh Nguyen"""

def print_girls(list_of_girls):
    
    for each_girl in list_of_girls:
        
        if isinstance(each_girl, list):
            
            print_girls(each_girl)
            
        else:
            
            print(each_girl)
