f = open('20_percent_for_tagging_100.csv', 'r')

train_set = []
for line in f.readlines(100):
    id_pair = ','.join(line.split(',')[0:2])
    train_set.append(id_pair)

f.close()

f = open('predict_results.csv', 'r')

for line in f.readlines():
	id_pair = ','.join(line.split(',')[0:2])
	if id_pair in train_set:
		continue

	print line.strip()