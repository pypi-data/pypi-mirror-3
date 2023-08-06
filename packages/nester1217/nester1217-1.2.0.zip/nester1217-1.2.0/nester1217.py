##-- recursion: while loop
##-- v1.1.0
##def print_list(the_list):
##  count=0
##  while count<len(the_list):
##    token=the_list[count]
##    if isinstance(token, list):
##      print_list(token)
##    else:
##      print(token)
##    count=count+1
##
##print_list(contact2)    # 改變引數內容即可
##---------------------------------
##-- recursion: while loop
##-- v1.1.1: add level arguement
##-- v1.2.0: define optional arguments
def print_list(the_list, level=0):
  count=0
  while count<len(the_list):
    token=the_list[count]
    if isinstance(token, list):
      print_list(token, level+1)
    else:
      print(token)
    count=count+1

##-- recursion: for loop
##--
##def print_list(the_list):
##  for each_item in the_list:
##    if isinstance(each_item, list):
##      print_list(each_item)
##    else:
##      print(each_item)
##
##print_list(contact2)    # 改變引數內容即可


##-- Non-recursion
##--
##for level1 in contact:
##  if isinstance(level1, list):
##    for level2 in level1:
##      if isinstance(level2, list):
##        for level3 in level2:
##          print("L3:", level3)
##      else:
##        print("L2:", level2)      
##  else:
##    print("L1:", level1)
