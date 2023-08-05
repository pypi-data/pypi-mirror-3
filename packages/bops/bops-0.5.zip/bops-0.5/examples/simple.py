from bops import *
import numpy as np

'''

          -------------------- DESCRIPTION -----------------------

This script gives an example as to how to use the bops' MapReduce functionality.

The script title may be a bit deceiving, however, simply due to the fact 
  that the map reduce paradigm is not yet widely known or used.
Many complex analysis principles are shown in the script below. Lack of 
  familiarity with python, it's syntax or simply having not used lists, 
  dictionaries or numpy arrays before will make this difficult to understand.

          ----------------------- NUMPY -----------------------

Numpy is used as the backbone to the bops module. Although, some of the MapReduce 
  functionality is in pure python, to gain performance consider using 
  the 'mapreducebatch' method. However, in the persuit of speed, the batch 
  method does add some complexity as well. For simplicity, the 'mapreduce' function
  may make things easier.

          --------------------- TEST DATA ---------------------

The test data used is a file with a list of 250000. 
The file has 5 columns:
  name, gender, age, years in college and number of friends

The test data was produced by 'test_data_gen.py'.

This data will be used to show the usefulness and conciseness of using bops for 
  MapReduce operations.

Several questions are asked about the data:
    1. How many college graduates are there for both genders, broken up by age group?
    2. What's the total number of college graduates for each gender?
    3. What's the total number of college graduates across both genders?

    NOTE: For simplicity, a college graduate is defined as someone who has 
      spent more than 4 years in college.

For more information on the MapReduce paradigm and algorithms, read the article 
  on Wikipedia.

'''

if __name__ == '__main__':

  print "\nComparing mapreducebatch and mapreduce functions.\n"

  # All lines in the file are read into the lines list
  # All lines are 'stripped', meaning any newlines are removed
  # All lines are then 'split' on commas, producing another list
  # Therefore the lines list is a 2d list representing the file.
  print "Reading data..."
  lines = []
  with open("people.csv", 'r') as f:
    f.readline()  #remove first line from file (header line)
    for line in f:
      lines.append(line.strip().split(','))
  
  # After the file has been read, the data is then put into a 'bop'. 
  # This class has several useful attributes for manipulating data. However,
  #   only the MapReduce portion will be covered in this script.
  # The constructor requires two arguments, the data and the column names.
  print "Aggregating data..."
  cols = 'name,gender,age,college,friends'
  data = bop(lines, cols)
  print

  print "\nUsing 'mapreducebatch' function:\n"+"-"*32
  print

  # Question 1.
  print "How many college graduates are there for both genders, broken up by age group?"

  # Define graduated
  # This is a reducer do be used on the data for each group after it has passed 
  #   through a map operation.
  # NOTE: All reducers used with the mapreducebatch method are given the entire 
  #   mapped data group
  # NOTE: All reducers not used with the mapreducebatch method are given each 
  #   element of the mapped data group
  # This reducer returns the numpber of ppl who have more than 4 years in college
  def graduated(data):
    return len(np.nonzero(data.college > 4)[0])
 
  # This is one attribute of the data describing the age groups that ppl belong to.
  # This basically determines the decade of your age. 
  # Simply put, if you are 35, it returns 30, for 58 it returns 50
  # This allows the data to be aggregated by ppl of similar age
  agegroup = data.age // 10 * 10

  # This is map reduce operation call
  # It finds all the unique combinations of gender and age group and passes 
  #   each unique group to the reducer separately.
  # If a reducer is left out, then the data returned is the raw data that belong to that group.
  # The 'expand' option makes the output easier to deal with, however, if you 
  #   only want a key/value pair to be returned, leave out this option.
  #The 'names' option are the column names to be returned
  gender_age_grad = data.mapreducebatch([data.gender, agegroup], reducer=graduated, expand=True, names='gender,agegroup,graduates')

  # This orders the data by gender and age group for ordered output.  
  gender_age_grad.orderby('gender','agegroup')

  # Output the results in a pretty fashion
  print
  print repr("Gender").rjust(7),repr("Age Group").rjust(4),repr(">4yrs in college").rjust(17)
  for gender, age, grad in gender_age_grad:
    print repr(gender).ljust(9),repr(age).ljust(11),repr(grad).ljust(17)
  print

  # Question 2.
  print "What's the total number of college graduates for each gender?"

  # This reducer sums all the counts from the previous map reduce
  # The previous map reduce job will produce something like this:
  #   [('F', 10, 978) 
  #    ('F', 20, 4830) 
  #    ('F', 30, 4796)
  #         ....
  #    ('M', 40, 11313)
  #    ('M', 50, 11264)
  #    ('M', 60, 11102)]
  # As you can see, all elements have the gender and age group as well as the count of college graduates
  # This reducer sums the graduate column for each gender
  def gender_graduates(group):
    return sum(group.graduates)

  # The mapper used only groups by gender and passes the list of counts to the reducer to sum
  # The results are also named by the columns: gender and graduates
  gender = gender_age_grad.mapreducebatch([gender_age_grad.gender], reducer=gender_graduates, names='gender,graduates')

  # print the results in a readable fashion
  print
  print repr("Gender").rjust(7),repr(">4yrs in college").rjust(17)
  for g, grads in gender:
    print repr(g).ljust(8),repr(grads).ljust(18)
  print

  # Question 3.
  print "What's the total number of college graduate across both genders?"

  # This mapper is not to be used with the batch as it is meant to be passed every element.
  # Because all elements are passed to it we can combine both genders as one map result named 'Both'
  def both_genders(group):
    return "Both", group.graduates

  # This map reduce job combine the genders and then sums the graduates from both genders
  mr = gender.mapreduce(both_genders, sum, expand=True)
  label, value = mr[0]

  #print the results
  print str(label).ljust(8),str(value).ljust(18),""


  def ga_mapper(row):
    return (row.gender, row.age // 10 * 10), row
  
  def grads(group):
    return sum([1 for p in group if p.college > 4])


  print "\nUsing 'mapreduce' function:\n"+"-"*27
  print

  gender_age_grad = data.mapreduce(ga_mapper, reducer=grads, expand=True, sort=True)
  for gender, age_group, grads in (gender_age_grad):
    print gender, age_group, grads

  # The following shows how to alias a function as a data attribute. This is a 
  # shorthand for calling a function for a given numpy array.
  # By applying the alias name=f, 'data.gender_name' is the same as 'f(data.gender)'.
  print "\nAlias example..."
  def f(array):
    gender = []
    for g in array:
      if g in 'F':
        gender.append('Female')
      else:
        gender.append('Male')
    return np.asarray(gender)
  
  data.alias(name=f)
  print data.gender_name

  print "Done."
