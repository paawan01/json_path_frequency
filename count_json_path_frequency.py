import os
import json
from pprint import pprint
# from collections import Counter

#######################################################
JSON_PATH = './test.json' # Path to JSON file containing the input
K = 2   # Top K values to display for leaf nodes
K_PRIME = 1  # For top K only consider fields having more occurences than K_PRIME
THRESH = 0.2  # The occurence fraction below which we need to filter the paths
DUMMY_ROOT = "*"  # A dummy path to have in all jsons so that implementation is easy for the first level
#######################################################


def is_primitive(thing):
    '''
    Reference - https://stackoverflow.com/questions/6391694/how-to-check-if-a-variables-type-is-primitive
    :param thing: object to check if it is of primtive type
    :return: boolean whether the thing is of primitive type or not.
    '''
    primitive = (int, float, long, str, bool, unicode)
    return isinstance(thing, primitive)


def get_nested_dict_val(nested_dict, nested_keys):
    '''
    Given a list of nested keys return the value of that from nested dictionary or a list
    :param nested_dict: nested dict or list to extract values from
    :param nested_keys: list of keys
    :return: object
    '''
    for key in nested_keys:
        if isinstance(nested_dict, list):
            nested_dict = nested_dict[int(key)]
        else:
            nested_dict = nested_dict[key]
    return nested_dict


def read_json(json_path):
    '''
    Function to read json object from file
    :param json_path: Absolute path to json file
    :return: Json object of the input file
    '''
    assert os.path.isfile(json_path)
    with open(json_path) as f:
        json_obj = json.load(f)

    return json_obj


def get_path_frequencies(json_collection, dummy_root=DUMMY_ROOT, K_for_topK=K, K_PRIME_for_topK=K_PRIME,\
                         threshold = THRESH, round_decimal_places=3):
    '''

    :param json_collection: Input JSON collection list
    :param dummy_root: The dummy key added so that we can BFS over the first level.
    :param K_for_topK: Top K values to display for leaf nodes
    :param K_PRIME_for_topK: For top K only consider fields having more occurences than K_PRIME
    :param threshold: The occurrence fraction below which we need to filter the paths
    :param round_decimal_places: Round the fraction to this many decimal places
    :return:
    '''

    ans = []  # List containing the set of answers
    num_jsons = float(len(json_collection))
    bfs_queue = []  # Queue for BFS.
    d = {}
    d['path'] = dummy_root
    d['indices'] = range(0, int(num_jsons))
    bfs_queue.append(d)

    while len(bfs_queue) != 0:
        # Continue till there's an element in the queue
        sub_ans = []
        d = bfs_queue.pop(0)  # extract first element.
        path = d['path']
        indices_for_path = d['indices']
        count_map = {}  # Hash map for maintaining count paths
        path_indices_map = {}  # Map which stores the indexes of where path occurs in list of JSONs

        for i in indices_for_path:
            primitive_path = False
            json_obj = json_collection[i]
            path_val = get_nested_dict_val(json_obj, path.split('/'))
            # print path_val
            if is_primitive(path_val):
                # If path_val is primitive then it's a leaf node - count the values for top k leaf nodes
                primitive_path = True
                # print "Primitive: ", path + '/' + str(path_val)
                key = str(path_val).lower()
                if key in count_map:
                    count_map[key] += 1
                else:
                    count_map[key] = 1

            else:
                for ind, k in enumerate(path_val):
                    if isinstance(path_val, dict):
                        key = k
                    elif isinstance(path_val, list):
                        key = str(ind)

                    if key in count_map:
                        count_map[key] += 1
                    else:
                        count_map[key] = 1
                        path_indices_map[key] = []
                    path_indices_map[key].append(i)

        if not primitive_path:
            if path != dummy_root: # Don't consider for dummy root
                sub_ans.append(path.split(dummy_root+'/')[-1])  # Remove the dummy_root/ from the path
                freq = len(indices_for_path)/num_jsons
                sub_ans.append(round(freq, round_decimal_places))
                sub_ans.append([])
                ans.append(sub_ans)

            for key in count_map:
                freq = count_map[key]/num_jsons
                if freq > threshold:  # Only add child to bfs queue if freq > threshold
                    d = {}
                    d['path'] = path + '/' + key
                    d['indices'] = path_indices_map[key]
                    bfs_queue.append(d)

        else:
            # If primitive path(leaf node) count top k occurrences.
            sub_ans.append(path.split(dummy_root + '/')[-1])
            freq = len(indices_for_path) / num_jsons
            sub_ans.append(round(freq, round_decimal_places))
            # Sort based on the decreasing order of occurrences.
            sorted_count_map = sorted(count_map.items(), key=lambda x: x[1], reverse=True)
            top_K = []
            for k, tup in enumerate(sorted_count_map):
                if k >= K_for_topK:
                    break
                cnt = tup[1]
                val = tup[0]
                if cnt < K_PRIME_for_topK:
                    break
                rel_freq = cnt/float(len(indices_for_path))
                top_K.append((val, round(rel_freq, round_decimal_places)))
            sub_ans.append(top_K)
            ans.append(sub_ans)
            # print count_map
        #print bfs_queue
    return ans


if __name__ == "__main__":
    json_collection = read_json(JSON_PATH)
    print "\n\nInput JSON Collection: "
    pprint(json_collection)
    edited_json_collection = []
    for j in json_collection:
        tmp = {}
        tmp[DUMMY_ROOT] = j
        edited_json_collection.append(tmp)

    ans = get_path_frequencies(edited_json_collection)
    print "\n\nOutput set (path, fraction of occurrences, top K most frequent values for leaf paths): "
    pprint(ans)
