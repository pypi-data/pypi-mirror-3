'''
Created on 2012-7-30

@author: hanjinqi
'''
def print_lol(the_list,isrun=flase,num=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,num+1)
        else:
            if(isrun):
                for tab_stop in range(num)
                    print('\t',end='')
            print(each_item)
