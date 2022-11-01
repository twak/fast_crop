import pandas as pd
import json
import matplotlib.pyplot as plt

def read(file):
    with open(file, 'r') as myfile:
        lines = myfile.readlines()

        s = ", ".join(lines)
        s = f"[{s}]"

        d = json.loads(s)

        df = pd.DataFrame(d)
    return df

dfl = read(r'/home/twak/Downloads/20221028_011829.log.json')
dfs = read(r'/home/twak/Downloads/20221028_204117.log.json')
#print (dfl)

fig = plt.figure(figsize=(12,5))

plt.plot(dfl['loss'], alpha=0.2, color="blue")
plt.plot(dfl.ewm(alpha=0.1).mean().loss, alpha=0.8, color="orange")

# plt.plot(dfs['loss'], alpha=0.2, color="green")
# plt.plot(dfs.ewm(alpha=0.1).mean().loss, alpha=0.8, color="red")


n = 500
ticks = [t for t in range(len(dfl)-1) if t % n == 0]
labels = [str ( int(l)) for i, l in enumerate(dfl["iter"][1:]) if i % n == 0]
plt.xticks( ticks, labels)

plt.show()


# plt.xlabel('Number of requests every 10 minutes')

# ax1 = df.x.plot(color='blue', x='iter', y='loss')
# ax2 = df.y.plot(color='red', x='iter', y='loss')
#
# ax1.legend(loc=1)
# ax2.legend(loc=2)
#
# plt.show()