'''
Created on 2012-7-3

@author: zzy
'''

#定义缩进打印列表
def print_level(the_list, level=0):
    for item in the_list:
        if isinstance(item, list):
            print_level(item, level + 1)
        else:
            for inc in range(level):
                print("\t", end="") #end表示print以''结尾，而不是换行
                inc  #为了不提示警告而写的无意义代码
            print(item)

