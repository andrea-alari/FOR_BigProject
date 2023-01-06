# Biogas plants location
a well known problem in operations research

by* Andrea Alari, Lorenzo Basile and Chiara Bordegari*

**The problem:**

An association of n farmers wants to open p plants to produce energy from biogas. Each plant will be opened at a farm of a member of the association and will be powered with corn chopping purchased from the farm itself or from other neighboring farms.

Each farm i can provide at most ci tons of corn chopping, with a percentage of dry matter ai. As you may know, dry matter is the key component of corn chopping used for biogas production. In order to maintain the quality of produced energy, each plant must burn a mixture of corn chopping with a percentage of dry matter between kmin and kmax.

At most one plant can be located in each farm, and every farm can sell its corn chopping to one and only one plant.

Each farm i is located at coordinates xi and yi, representing respectively its latitude and longitude, and the cost of moving corn chopping from a farm i to a farm j is proportional to the euclidean distance between the two farms (it does not depend on the actual quantity moved, since the trucks used for this transportations are sufficiently big).


Under such conditions, every plant produces Q kWh of energy per ton of corn chopping burned. The energy produced by each plant will be fed into the national electricity system, at a unitary price of b (€/kWh). Moreover, due to state regulations, each plant must not produce more than M kWh of energy.

You must locate p plants among the available farms and assign the farms that will supply each plant, with the goal of maximizing the total revenues of the association.

[Link to a python notebook with further explanation](https://colab.research.google.com/drive/1WhTuk2VP8ku4RIJpJdG_GsRJDKMswS6N?usp=sharing "Link to a python notebook with further explanation")
