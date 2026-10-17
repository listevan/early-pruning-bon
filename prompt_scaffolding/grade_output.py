import json
import sys

# usage: python grade_output.py RESULT.json  (March-era 3-element results schema)
with open(sys.argv[1], 'r') as file:
    data = json.load(file)

data_8 = data['8']

total_score = 0
for i in range(len(data_8['results'])):
    if data_8['results'][i][2] == 1.0:
        print("==== Wrong response below:")
        print(data_8["responses"][i][0]["text"])
        print("\n")
    total_score += data_8['results'][i][2]
    

print("=========== Total Accuracy: =============")
print(float(total_score) / float(len(data_8['results'])))
print()

print("=========== Generating Index-selection frequency Histogram =============")
print(data_8['indexes'])
print()

from collections import Counter
import matplotlib.pyplot as plt
flat_list = [item for sublist in data_8['indexes'] for item in sublist]

counts = Counter(flat_list)

labels = list(range(1, 9))
frequencies = [counts.get(i, 0) for i in labels]

plt.bar(labels, frequencies, color='lightcoral', edgecolor='black')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Frequency of Individual Numbers (Range 1-8)')
plt.xticks(labels)
plt.savefig('number_frequency_histogram.png')