# gitply
Simple script for visualizing the contributions of each contributor to a repository

## Requirements

- Python (works on 2.7.11+, hangs for some reason on 3.5.1+ -- investigation pending)
- numpy
- matplotlib

## Usage

To generate per-user commit statistics, pass this script the location of a git
repository. You can also list several repos, and the commits from each will be
combined.

The default behavior is to print out a history that looks like this (email addresses
shown modified in order to prevent spam):

    $ python gitply.py .
    History for lq at le1 dot ca
      2016, week 23:  1 commits, +112  -0   

    History for root at lo dot calho dot st
      2016, week 23:  1 commits, +324  -0   
  
Notice that my two commits appear under two different email addresses. To combine
them into one actual user, this software supports reading a "user map" from a
file. For example:

    $ python gitply.py . --users usermap_example.txt 
    History for le1ca
      2016, week 23:  2 commits, +436  -0  

You can see how the user map is formatted by viewing the copy of usermap_example.txt
included here in this repository.

You can also generate a plot using gitply -- use the --pdf parameter to specify
where the plot will go. 

Here's an example using a different repository (contributors anonymized):

    $ python gitply.py ~/Zeall/backend --users user_map2.txt --pdf example.pdf
    History for anon4
      2015, week 32:  1 commits, +2    -0   
      -- Gap of 2 weeks
      2015, week 35:  4 commits, +182  -1   
      2015, week 36:  2 commits, +461  -49  
      -- Gap of 2 weeks
      2015, week 39:  6 commits, +856  -361 
      2015, week 40:  2 commits, +668  -291 
      2015, week 41:  3 commits, +585  -198 
      2015, week 42:  3 commits, +278  -76  
      2015, week 43:  6 commits, +161  -50  
      -- Gap of 1 week
      2015, week 45:  2 commits, +165  -41  

    History for anon3
      2015, week 32: 10 commits, +503  -24  
      2015, week 33: 38 commits, +2028 -790 
      2015, week 34: 15 commits, +2163 -960 
      2015, week 35: 51 commits, +2438 -415 
      2015, week 36: 25 commits, +669  -167 
      2015, week 37: 53 commits, +1821 -162 
      2015, week 38: 25 commits, +819  -41  
      2015, week 39: 32 commits, +889  -103 
      2015, week 40: 44 commits, +508  -100 
      2015, week 41: 15 commits, +440  -363 
      2015, week 42: 11 commits, +244  -104 
      -- Gap of 1 week
      2015, week 44:  8 commits, +102  -16  
      2015, week 45:  1 commits, +221  -21  
      2015, week 46:  2 commits, +60   -12  
      2015, week 47: 20 commits, +517  -197 
      -- Gap of 1 week
      2015, week 49: 20 commits, +373  -67  
      2015, week 50: 10 commits, +190  -14  
      2015, week 51: 21 commits, +1032 -252 
      2015, week 52: 12 commits, +108  -42  
      -- Gap of 1 week
      2016, week  1:  5 commits, +20   -3   
      -- Gap of 1 week
      2016, week  3: 11 commits, +332  -48  
      2016, week  4:  3 commits, +34   -14  
      -- Gap of 1 week
      2016, week  6: 14 commits, +311  -178 
      2016, week  7: 22 commits, +409  -142 
      2016, week  8:  9 commits, +263  -181 
      2016, week  9: 10 commits, +292  -144 
      2016, week 10:  6 commits, +154  -33  
      2016, week 11: 19 commits, +129  -112 
      2016, week 12:  8 commits, +43   -12  
      2016, week 13:  2 commits, +0    -3   
      2016, week 14:  9 commits, +2133 -2139
      2016, week 15:  1 commits, +9    -2   
      2016, week 16:  2 commits, +111  -111 
      2016, week 17: 14 commits, +9700 -10052
      2016, week 18:  6 commits, +2075 -176 
      -- Gap of 1 week
      2016, week 20: 14 commits, +386  -398 
      2016, week 21:  7 commits, +507  -24  
      2016, week 22:  8 commits, +145  -10  
      2016, week 23: 12 commits, +2015 -1834

    History for anon2
      2016, week  6:  2 commits, +366  -26  
      2016, week  7:  4 commits, +325  -5   
      2016, week  8:  2 commits, +224  -3   
      2016, week  9: 21 commits, +2617 -219 
      -- Gap of 2 weeks
      2016, week 12: 10 commits, +4066 -614 
      2016, week 13:  6 commits, +2480 -432 
      2016, week 14:  2 commits, +654  -490 
      -- Gap of 1 week
      2016, week 16:  2 commits, +661  -229 
      -- Gap of 2 weeks
      2016, week 19:  3 commits, +1508 -47  
      -- Gap of 2 weeks
      2016, week 22:  1 commits, +1490 -29  

    History for anon1
      2016, week 12:  1 commits, +143  -89  
      2016, week 13:  2 commits, +58   -16  
      2016, week 14:  3 commits, +137  -17  
      2016, week 15:  2 commits, +403  -106 
      -- Gap of 2 weeks
      2016, week 18:  5 commits, +134  -38  
      -- Gap of 3 weeks
      2016, week 22:  1 commits, +13   -1   
      2016, week 23:  1 commits, +485  -1   

The plot in example.pdf looks like this:

![Example plot](/example.png)

In the actual PDF file, each user's plot is on a different page.

If you don't want the textual output, and only the PDF, you can also supply
the --noprint option.
