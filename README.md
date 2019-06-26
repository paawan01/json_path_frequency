
## Table of Contents

1. [Problem Statement](#problem_statement)
2. [File Descriptions](#files)
3. [Assumptions](#assumptions)
4. [Approach](#approach)
5. [Further optimizations](#optimizations)


## Problem Statement <a name="problem_statement"></a>

Given a set of json objects, output the set of (path, fraction of occurrences in the input set, top K most frequent values for leaf paths). For each path that is observed in the input set of JSON documents, we need to compute how often that path exists and when it exists what are the top K (say, 2) values along with their occurrence fractions – consider only values which occur at least K’ times (1 in the following example).

Consider the following collection of JSON documents.

{“name” : “Joe”, “address” : {“street” : “montgomery st”, “number”: 101, “city”: “new york”, “state”: “ny”}}  
{“name” : “Evan”, “address” : {“street” : “Santa Theresa st”, “number”: 201, “city”: “sfo”, “state”: “ca”}}  
{“name” : “Joe”, “address” : {“street” : “new hampshire ave”, “number”: 301, “city”: “dublin”, “state”: “ca”}}  
{“name” : “Joe”, “qualifications” : [“BS”, “MS”] }

The paths, percentages, and top values are:

[“name”, 1, [{Joe, 3⁄4}, {Evan, 1⁄4}],  
“address”, 3⁄4 \[] \(not a leaf path and hence we don’t consider the top K most frequent values)  
“qualifications”, 1⁄4, []  
“qualifications/0”, 1⁄4, [{“BS”, 1}]  
“qualifications/1”, 1⁄4, [{“MS”, 1}]  
“address/city”, 3⁄4, [{"new york", 1/3}, {"sfo", 1/3}]  
And, so on.

**Extension**: Consider an extension of the above problem where we only want paths and their top K frequent values when the occurrence fraction of a path is greater than a threshold (e.g., 0.30). Therefore, in the above example the paths {qualifications} would be left out. Consider scenarios where this threshold is high enough that most paths are disqualified, and the number of input json objects is very high.


## File Descriptions <a name="files"></a>
The code is written in python 2.7 and requires no extra modules/libraries to be installed.  
Files in the repo are as follows:
```count_json_path_frequency.py``` This is main file containing the logic to solve the above problem.  
To run it just use the command - 
```
python count_json_path_frequency.py
```

``` test.json```  A sample json to test the code (containing slight modification of same example as in the problem statement).


## Assumptions<a name="assumptions"></a>

The code written assumes the following points - 
1) The sub iterable objects or values of keys in the JSON collection can be list and dictionary and other primitives. The primitives (there is actually no notion of primitves in python) currently are defined as (int, float, long, str, bool, unicode) and can be eaisly extended to include other types.

2) Each key will have same type of value across JSONS in the collection. 
For instance if ```“address”``` key has the value : ```{“street” : “montgomery st”, “number”: 101, “city”: “new york”, “state”: “ny”}``` in one JSON, 
```“address” : "12thStreet" ```is not allowed since the type has changed from dictionary to a primtive string.
But structure change in same dictionary is allowed.  
In above example ```“address” : {new_field : “montgomery st”, “state”: “ny”}``` is perfectly okay to have along with the ```“address” : {“street” : “montgomery st”, “number”: 101, “city”: “new york”, “state”: “ny”}```

3) Case insensitive entries for keys and values: "Joe" "JOE" "joe" "JoE" "jOe" are all treated as same.

4) No path or field has "\*" as an name.


## Approach<a name="approach"></a>

### Brute force - 
The brute force or the obvious approach is to calculate the frequency of occurence of all the fields using a hashmap by iteratively moving over each JSON object in collection one by one and remove the entries which has occurence fraction less than the given threshold. 
This though works perfectly well in practice can be optimised drastically especially for the given extension case in problem.

### Optimised approach - 
The part that could be optimised in the previous approach is that if a parent key occurs less than the threshold in all the JSONs then the child keys or paths which can be reached via this keys can only occur at most this many times and eventually will have to be filtered out at the end. Hence we can avoid computing the occurences for such paths. 

For eg - if ```“address”``` key has the value like this : ```{“street” : “montgomery st”, “number”: 101, “city”: “new york”, “state”: “ny”}``` and ```"address"``` occurs less than the threshold in the collection then all paths from address i.e ```“address/street”```, ```“address/number”```, ```“address/city”```, ```“address/state”``` will also occur at most the times “address” occurs and can be skipped without even counting their actual occurence fraction.

How we do that in implementation is we take a Breadth First Search (BFS) kind of approach. We first move to one level and compute the occurence fractions and only add those subsequent child paths in the queue if the parent occurence fraction is greater than threshold.

Metaphorically speaking the Brute force represents Depth First Search (DFS) equivalence and the optimised one in terms of BFS.
This repo contains only the code for the optimised approach.


## Further optimizations<a name="optimizations"></a>

For maintaining the top-k occurences of leaf node, we're currently using sorting to sort the occurences in decreasing order and then push out top K values. This takes the complexity of O(n\*log(n)) where n is the number of JSONs in the collection.  
This could be eaisly optimised with a priority queue only containing top k values at a given point. Then the complexity would be of O(n\*log(k)) and since in practice k << n, this could theoritically be stated as O(n).

