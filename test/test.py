import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#plt.close("all")

ts = pd.Series(np.random.randn(1000), index=pd.date_range("1/1/2000", periods=1000))

ts = ts.cumsum()

ts.plot();

df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index, columns=list("ABCD"))

df = df.cumsum()

plt.figure();

df.plot();

df3 = pd.DataFrame(np.random.randn(1000, 2), columns=["B", "C"]).cumsum()

df3["A"] = pd.Series(list(range(len(df))))

df3.plot(x="A", y="B");

plt.figure();

df.iloc[5].plot(kind="bar");

#df = pd.DataFrame()
#
#df.plot.<TAB>  # noqa: E225, E999
#
#plt.figure();
#
#df.iloc[5].plot.bar();
#
#plt.axhline(0, color="k");
#
#df2 = pd.DataFrame(np.random.rand(10, 4), columns=["a", "b", "c", "d"])
#
#df2.plot.bar();
#
#df2.plot.bar(stacked=True);
#
#df2.plot.barh(stacked=True);
#
#df4 = pd.DataFrame(
#    {
#        "a": np.random.randn(1000) + 1,
#        "b": np.random.randn(1000),
#        "c": np.random.randn(1000) - 1,
#    },
#    columns=["a", "b", "c"],
#)
#plt.figure();
#
#df4.plot.hist(alpha=0.5);
#
#plt.figure();
#
#df4.plot.hist(stacked=True, bins=20);
#
#plt.figure();
#
#df4["a"].plot.hist(orientation="horizontal", cumulative=True);