from bops import *
import numpy as np
import time

'''
This script compares the numpy mapreduce implmentation verses the pure python implementation.

Rough testing reveals ~6x boost using numpy.

'''

if __name__ == '__main__':

  times = []
  fast = True
  pure = True
  sandbox = True

  print "Reading data..."
  lines = []
  with open("people.csv", 'r') as f:
    f.readline()  #remove first line from file (header line)
    for line in f:
      lines.append(line.strip().split(','))
  
  print "Aggregating data..."
  cols = 'name,gender,age,college,friends'
  data = bop(lines, cols)

  if fast:
    t1 = time.clock()
    friendgroup = data.friends // 100 * 100
    agegroup = data.age // 10 * 10

    gender_age_friends = data.mapreducebatch([data.gender, agegroup, friendgroup], reducer=len, expand=True, names='gender,agegroup,friendgroup,group')

    # This orders the data by gender and age group for ordered output.
    gender_age_friends.orderby('gender','agegroup', 'friendgroup')
    elapsed = (time.clock() - t1)
    print "batch: %0.2fs" % elapsed
    times.append("batch: %0.2fs" % elapsed)

    # Output the results in a pretty fashion
    print
    print repr("Gender").rjust(7),repr("Age Group").rjust(11),repr("Popularity").ljust(11),repr("Counts").ljust(7)
    for gender, age, friend, group in gender_age_friends:
      print repr(gender).ljust(9),repr(age).ljust(11),repr(friend).ljust(12),repr(group).ljust(7)
    print

  #pure python
  if pure:
    t1 = time.clock()
    def gaf_mapper(item):
    	return (item.gender, item.age // 10 * 10, item.friends // 100 * 100), item

    gender_age_friends = data.mapreduce(mapper=gaf_mapper, reducer=len, expand=True, sort=True)

    elapsed = (time.clock() - t1)
    print "pure: %0.2fs" % elapsed
    times.append("pure: %0.2fs" % elapsed)

    # Output the results in a pretty fashion
    print
    print repr("Gender").rjust(7),repr("Age Group").rjust(11),repr("Popularity").ljust(11),repr("Counts").ljust(7)
    for gender, age, friend, group in gender_age_friends:
      print repr(gender).ljust(9),repr(age).ljust(11),repr(friend).ljust(12),repr(group).ljust(7)
    print

  # sandbox for testing
  if sandbox:
    print "\nPopularity Analysis...\n"

    def pop_mapper(person):
      pops = ['0 - Unsocial/New', '1 - Outcasts', '2 - Groupie', '3 - Known Of', '4 - F & C Crowd']
      gender = ''
      if person.gender == 'F': gender = 'Female'
      else: gender = 'Male'
      return (gender, pops[person.friends // 100]), 1 # person

    def print_pop_summary(pop_classes):
      lens = []
      for c in range(len(pop_classes[0])):
        lens.append(max([len(str(t[c])) for t in pop_classes]) + 3)
      for row in pop_classes:
        s = ','.join([repr(col).ljust(lens[i]) for i, col in enumerate(row)])
        print s
      print

    print "\nAll Ages:"
    pop_class = data.mapreduce(pop_mapper, sum, expand=True, sort=True)
    print_pop_summary(pop_class)

    print "\nAll Females <= 25 yrs old"
    young = data.select((data.age <= 25) * (data.gender == 'F'))
    pop_class = young.mapreduce(pop_mapper, sum, expand=True, sort=True)
    print_pop_summary(pop_class)

  print "\nMapReduce Comparison\n"
  for t in times:
    print t

  print "\nDone."
